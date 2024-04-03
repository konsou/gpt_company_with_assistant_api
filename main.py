from assistants.open_ai import OpenAIAssistant
from assistants.open_router import OpenRouterAssistant
from instructions import DEVELOPER_INSTRUCTIONS
from message_bus import MessageBus, Message
from text import print_system_message

from workspace import DockerWorkspace


def handle_message(message):
    print_system_message(f"Received message from: {message.sender}")
    print_system_message(message.content)


def send_message(content, message_bus):
    message_bus.publish(
        Message(
            sender="konso",
            recipient="Erkki",
            content=content,
        )
    )


def main():
    message_bus = MessageBus()
    workspace = DockerWorkspace()

    ass = OpenRouterAssistant(
        # models=["databricks/dbrx-instruct", "mistralai/mixtral-8x7b-instruct"],
        # model="mistralai/mixtral-8x7b-instruct",
        model="anthropic/claude-3-haiku:beta",
        name="Erkki",
        role="Software Developer",
        instructions=DEVELOPER_INSTRUCTIONS,
        message_bus=message_bus,
        workspace=workspace,
    )
    message_bus.subscribe("konso", handle_message)

    while True:
        s = input("konso: ")
        if s.strip():
            send_message(content=s, message_bus=message_bus)
        ass.process_messages()


if __name__ == "__main__":
    main()
