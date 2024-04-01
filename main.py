from assistants.open_ai import OpenAIAssistant
from assistants.open_router import OpenRouterAssistant
from instructions import DEVELOPER_INSTRUCTIONS
from message_bus import MessageBus, Message

from workspace import DockerWorkspace

# TODO: command execution is wonky. Directory confusion?


def handle_message(message):
    print(f"Received message from: {message.sender}")
    print(message.content)


def main():
    message_bus = MessageBus()
    workspace = DockerWorkspace()

    ass = OpenRouterAssistant(
        model="databricks/dbrx-instruct",
        name="Erkki",
        role="Software Developer",
        instructions=DEVELOPER_INSTRUCTIONS,
        message_bus=message_bus,
        workspace=workspace,
    )
    message_bus.subscribe("konso", handle_message)
    message_bus.publish(
        Message(
            sender="konso",
            recipient="Erkki",
            content="Please create a test file in your dev env and then check the directory contents",
        )
    )


if __name__ == "__main__":
    main()
