import os
import time
import traceback
from typing import TypedDict, Optional, NamedTuple, Callable, Collection, Literal

import requests
import json

import message_bus
import workspace
from assistants.base import BaseAssistant, InternalMessage
from . import types_response
from ..tools.types import ToolCall


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
        self._messages: list[InternalMessage] = [
            {"role": "system", "content": self.instructions}
        ]
        self._api_request_headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

    def handle_bus_message(self, message: message_bus.Message):
        if message.recipient == self.name:
            self._add_bus_message(message)

    def _add_internal_message(self, message: InternalMessage):
        print(f"{self.name} received message: {json.dumps(message)}")
        self._messages.append(message)

    def _add_response_message(self, message: types_response.Message):
        if message["role"] in ("user", "assistant", "system", "tool"):
            role = message["role"]
        else:
            print(
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
        self, messages: list[InternalMessage]
    ) -> Optional[types_response.Response]:
        models = [self.model] if self.model is not None else self.models
        data = json.dumps(
            {
                "models": models,
                "messages": messages,
                "route": "fallback",
            }
        )

        print(f"Sending request to {API_URL}...")
        tries = 3
        retry_delay = 1
        while tries:
            response = requests.post(
                API_URL, headers=self._api_request_headers, data=data
            )

            try:
                response_data = response.json()
            except requests.exceptions.JSONDecodeError:
                print(f"Couldn't parse response")
                print(response.text)
                response_data = None

            if (
                response.status_code == 200
                and response_data
                and "error" not in response_data
            ):
                print(f"API call used model: {response_data['model']}")
                return response_data
            print(f"Request failed: {response.status_code}")
            if response_data:
                print(response_data)
            print(f"Retrying...")
            tries -= 1
            time.sleep(retry_delay)
        print(f"No response from API")
        return None

    def process_messages(self):
        response = self._make_api_request(self._messages)
        if response is None:
            print(f"{self.name}: response was empty")
            return
        response_message: types_response.Message = self._parse_response(response)
        if not response_message["content"]:
            print(f"{self.name}: response message was empty")
            return
        self._add_response_message(response_message)
        tool_calls = self.parse_tool_calls(
            response_message["content"], caller=self.name
        )
        self.call_tools(tool_calls)

    def call_tools(self, calls: Collection[ToolCall]):
        for tool_call in calls:
            self._add_internal_message(
                {
                    "role": "tool",
                    "content": f'Running tool "{tool_call.tool.name}" with arguments {tool_call.args} '
                    f"and keyword arguments {tool_call.kwargs}",
                }
            )
            result = tool_call.call()
            self._add_internal_message(
                {
                    "role": "tool",
                    "content": f"Tool run result: ```{result}```",
                }
            )

    def _parse_response(
        self, response: types_response.Response
    ) -> Optional[types_response.Message]:
        try:
            return response["choices"][0]["message"]
        except (KeyError, TypeError):
            print(f"Invalid response")
            print(f"Response was:\n{response}")
            return None

    def get_response_from_query(self, asker_name: str, query: str) -> str:
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "name": asker_name, "content": query},
        ]

        response_data = self._make_api_request(messages)

        try:
            response_text = response_data["choices"][0]["message"]["content"]
        except (KeyError, TypeError) as e:
            print(f"Invalid response")
            traceback.print_exc()
            print(f"Response was:\n{response_data}")
            return ""

        commands: list[str] = self.parse_execute_commands(response_text)
        for command in commands:
            command_result = self.run_command(command)
            response_text += "\nCommand result: " + command_result.content

        return response_text
