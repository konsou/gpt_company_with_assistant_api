import os
import sys
import time

import dotenv
import openai

dotenv.load_dotenv()


class OpenAIAssistant:
    def __init__(self, model, name, instructions):
        self._api_key = os.getenv('OPENAI_API_KEY')
        self.model = model
        self.name = name
        self.instructions = instructions
        self._client = openai.Client(api_key=self._api_key)
        self._assistant = self._client.beta.assistants.create(model=model, name=name, instructions=instructions)
        self._threads: dict[str, object] = {}

    def get_response(self, asker_name: str, query: str) -> str:
        if asker_name not in self._threads:
            self._create_thread(asker_name)

        thread = self._threads[asker_name]

        message = self._client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        run = self._client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._assistant.id,
        )

        self._wait_for_run(thread=thread, run=run)

        messages = self._client.beta.threads.messages.list(
            thread_id=thread.id
        )

        return messages.data[0].content[0].text.value

    def _wait_for_run(self, thread, run):
        while True:
            run = self._client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run.status == 'queued' or run.status == 'in_progress':
                time.sleep(0.5)
                continue
            elif run.status == 'completed':
                break
            else:
                print(f"Run status: {run.status}")
                sys.exit(1)

    def _create_thread(self, asker_name: str) -> None:
        self._threads[asker_name] = self._client.beta.threads.create()
