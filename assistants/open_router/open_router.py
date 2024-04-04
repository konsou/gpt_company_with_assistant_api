import os
import time
import traceback
from typing import TypedDict, Optional, NamedTuple, Callable, Collection, Literal

import requests
import json

import message_bus
import workspace
from assistants.base import BaseAssistant, InternalMessage
from text import print_info, print_warning, print_error
from . import types_response
from ..tools.abc import ToolCall


API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterAssistant(BaseAssistant):
    def __init__(
        self,
        name: str,
        role: str,
        instructions: str,
        message_bus: message_bus.MessageBus,
        workspace: workspace.Workspace,
        model: Optional[str] = None,
        models: Optional[list[str]] = None,
    ):
        super().__init__(
            model=model,
            models=models,
            name=name,
            role=role,
            instructions=instructions,
            message_bus=message_bus,
            workspace=workspace,
        )
        self._api_key = os.getenv("OPENROUTER_API_KEY")
        if not self._api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        self._messages: list[InternalMessage] = [
            {"role": "system", "content": self.instructions}
        ]
        self._api_request_headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        # Force model change or crash after this many empty messages
        self.empty_message_limit = 3
        self._empty_messages_by_model: dict[str, int] = (
            {self.model: 0} if self.model else {m: 0 for m in self.models}
        )

    def handle_bus_message(self, message: message_bus.Message):
        if message.recipient == self.name:
            self._add_bus_message(message)

    def _add_internal_message(self, message: InternalMessage):
        print(f"{self.name} received message: {json.dumps(message)}")
        self._merge_or_add_message(message)

    def _merge_or_add_message(self, message: InternalMessage):
        """OpenRouter API doesn't like multiple "user" role messages in a row.
        Apparently "tool" messages are counted as "user" role messages as well."""
        new_message = message
        user_roles = ("user", "tool")
        last_stored_message = self._messages[-1]
        if (
            new_message["role"] in user_roles
            and last_stored_message["role"] in user_roles
        ):
            print_info(f"Two consecutive 'user' role messages detected, merging...")
            last_stored_message_name = self._get_message_user_name(last_stored_message)
            new_message_name = self._get_message_user_name(new_message)

            merged_message: InternalMessage = {
                "role": "user",
                "content": f"{last_stored_message_name}: {last_stored_message['content']}\n"
                f"{new_message_name}: {new_message['content']}",
            }
            self._messages[-1] = merged_message
        else:
            self._messages.append(new_message)

    def _get_message_user_name(self, message: InternalMessage) -> str:
        default = message["role"].capitalize()
        return message.get("name", default)

    def _add_response_message(self, message: types_response.Message):
        if message["role"] in ("user", "assistant", "system", "tool"):
            role = message["role"]
        else:
            print_warning(
                f"Invalid role in response: {message['role']}. Changing to \"assistant\"."
            )
            role = "assistant"

        # pyCharm doesn't understand the code above that ensures "role" type
        # noinspection PyTypeChecker
        m: InternalMessage = {
            # noinspection
            "role": role,
            "content": message["content"] if message["content"] is not None else "",
        }
        self._add_internal_message(m)

    def _add_bus_message(self, message: message_bus.Message):
        m: InternalMessage = {
            "role": "user",
            "name": message.sender,
            "content": message.content,
        }
        self._add_internal_message(m)

    def _make_api_request(
        self, messages: list[InternalMessage], override_model: Optional[str] = None
    ) -> Optional[types_response.Response]:
        if override_model is not None:
            models = [override_model]
        else:
            models = [self.model] if self.model is not None else self.models
        data = json.dumps(
            {
                "models": models,
                "messages": messages,
                "route": "fallback",
            }
        )

        print_info(f"Sending request to {API_URL}...")
        tries = 3
        retry_delay = 1
        while tries:
            response = requests.post(
                API_URL, headers=self._api_request_headers, data=data
            )

            try:
                response_data = response.json()
            except requests.exceptions.JSONDecodeError:
                print_error(f"Couldn't parse response")
                print(response.text)
                response_data = None

            if (
                response.status_code == 200
                and response_data
                and "error" not in response_data
            ):
                print_info(f"API call used model: {response_data['model']}")
                return response_data
            print_error(f"Request failed: {response.status_code}")
            if response_data:
                print(response_data)
            print_info(f"Retrying...")
            tries -= 1
            time.sleep(retry_delay)
        print_error(f"No response from API")
        return None

    def select_override_model(self) -> Optional[str]:
        if self.model is not None:
            model = self.model
            num_models = 1
        else:
            model = self.models[0]
            num_models = len(self.models)
        empty_messages = self._empty_messages_by_model[model]
        if empty_messages <= self.empty_message_limit:
            # No need for model override, all is well
            return None

        if num_models == 1:
            raise RuntimeError(
                f"Model {model} sent too many ({empty_messages}) empty messages - no alternatives"
            )
        else:
            override_model = self.models[1]
            print_warning(
                f"Model {model} sent too many ({empty_messages}) empty messages - overriding temporarily with {override_model}"
            )
            # Need to decrement counter, or we will never return to the original model
            self._empty_messages_by_model[model] -= 1
            return override_model

    def process_messages(self):
        print_info(f"{self.name} processing messages...")
        override_model = self.select_override_model()
        response = self._make_api_request(self._messages, override_model=override_model)
        if response is None:
            print_warning(f"{self.name}: response was empty")
            return
        response_message: types_response.Message = self._parse_response(response)
        if not response_message["content"]:
            print_warning(
                f"{self.name}: response message from {response['model']} was empty"
            )
            self._empty_messages_by_model[response["model"]] += 1
            return
        self._empty_messages_by_model[response["model"]] = 0
        self._add_response_message(response_message)
        tool_calls = self.parse_tool_calls(
            response_message["content"], caller=self.name
        )
        if len(tool_calls) > 1:
            print_warning("Multiple tags detected")
            self._add_internal_message(
                {
                    "role": "tool",
                    "content": "Warning: multiple tags detected. "
                    "Running the first, discarding others.",
                }
            )
        if len(tool_calls) < 1:
            print_warning("No tags detected")
            self._add_internal_message(
                {
                    "role": "tool",
                    "content": "Warning: no tags detected. "
                    "Use <message> tags for communication.",
                }
            )
        # Only support one tool call per message
        self.call_tools(tool_calls[:1])

    def call_tools(self, calls: Collection[ToolCall]):
        for tool_call in calls:
            self._add_internal_message(
                {
                    "role": "tool",
                    "content": f')Running tool "{tool_call.tool.name}" with arguments {tool_call.args} '
                    f"and keyword arguments {tool_call.kwargs}",
                }
            )
            result = tool_call.call()
            self._add_internal_message(
                {
                    "role": "tool",
                    "content": f'Tool run result: "{result}"',
                }
            )

    def _parse_response(
        self, response: types_response.Response
    ) -> Optional[types_response.Message]:
        try:
            return response["choices"][0]["message"]
        except (KeyError, TypeError):
            print_error(f"Invalid response")
            print(f"Response was:\n{response}")
            return None
