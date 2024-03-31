import os

import requests
import json

import message_bus
import workspace
from .base import BaseAssistant


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

    def handle_message(self, message: message_bus.Message):
        if message.recipient == self.name:
            response = self.get_response(message.sender, message.content)
            self.message_bus.publish(
                message_bus.Message(
                    sender=self.name, recipient=message.sender, content=response
                )
            )

    def get_response(self, asker_name: str, query: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        data = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "name": asker_name, "content": query},
                ],
            }
        )

        print(f"Sending request to {url}...")
        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()

        return response_data["choices"][0]["message"]["content"]
