import os
import time
import traceback
from typing import TypedDict, Optional

import requests
import json

import message_bus
import workspace
from assistants.base import BaseAssistant
from . import types


Message = dict[str, str]


API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterAssistant(BaseAssistant):
    def __init__(
        self,
        model: str,
        name: str,
        role: str,
        instructions: str,
        message_bus: message_bus.MessageBus,
        workspace: workspace.Workspace,
    ):
        super().__init__(
            model=model,
            name=name,
            role=role,
            instructions=instructions,
            message_bus=message_bus,
            workspace=workspace,
        )
        self._api_key = os.getenv("OPENROUTER_API_KEY")
        self._messages: list[Message] = [
            {"role": "system", "content": self.instructions}
        ]
        self._api_request_headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

    def handle_message(self, message: message_bus.Message):
        if message.recipient == self.name:
            self._add_message_bus_message(message)
            response = self.get_response_from_query(message.sender, message.content)
            self.message_bus.publish(
                message_bus.Message(
                    sender=self.name, recipient=message.sender, content=response
                )
            )

    def _add_internal_message(self, message: Message):
        self._messages.append(message)

    def _add_message_bus_message(self, message: message_bus.Message):
        m: Message = {
            "role": "user",
            "name": message.sender,
            "content": message.content,
        }
        self._add_internal_message(m)

    def _make_api_request(self, messages: list[Message]) -> Optional[types.Response]:
        data = json.dumps(
            {
                "model": self.model,
                "messages": messages,
            }
        )
        print(f"Sending request to {API_URL}...")
        tries = 3
        retry_delay = 1
        while tries:
            response = requests.post(
                API_URL, headers=self._api_request_headers, data=data
            )
            response_data = response.json()
            if (
                response.status_code == 200
                and response_data
                and "error" not in response_data
            ):
                return response_data
            print(f"Request failed: {response.status_code}")
            if response_data:
                print(response_data)
            print(f"Retrying...")
            tries -= 1
            time.sleep(retry_delay)
        print(f"No response from API")
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
