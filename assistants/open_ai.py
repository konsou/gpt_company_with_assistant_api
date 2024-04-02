import os
import sys
import time
from typing import Any

import dotenv
import openai
import openai.types.beta.threads

from .base import BaseAssistant
import message_bus
import workspace

dotenv.load_dotenv()


class OpenAIAssistant(BaseAssistant):
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
        self._api_key = os.getenv("OPENAI_API_KEY")
        self._client = openai.Client(api_key=self._api_key)
        self._assistant = self._client.beta.assistants.create(
            model=model, name=name, instructions=instructions
        )
        self._threads: dict[str, object] = {}

    def handle_bus_message(self, message: message_bus.Message):
        if message.recipient == self.name:
            response = self.get_response(message.sender, message.content)
            self.message_bus.publish(
                message_bus.Message(
                    sender=self.name, recipient=message.sender, content=response
                )
            )

    def get_response(self, asker_name: str, query: str) -> str:
        if asker_name not in self._threads:
            self._create_thread(asker_name)

        thread = self._threads[asker_name]

        message: openai.types.beta.threads.Message = (
            self._client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=query
            )
        )

        run = self._client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._assistant.id,
        )

        self._wait_for_run(thread=thread, run=run)

        messages = self._client.beta.threads.messages.list(thread_id=thread.id)

        return messages.data[0].content[0].text.value

    def _wait_for_run(self, thread: Any, run: Any):
        while True:
            run = self._client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            if run.status == "queued" or run.status == "in_progress":
                time.sleep(0.5)
                continue
            elif run.status == "completed":
                break
            else:
                print(f"Run status: {run.status}")
                sys.exit(1)

    def _create_thread(self, asker_name: str) -> None:
        self._threads[asker_name] = self._client.beta.threads.create()
