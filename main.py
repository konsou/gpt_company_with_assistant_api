import text
from assistants.open_router import OpenRouterAssistant
from instructions import DEVELOPER_INSTRUCTIONS
from message_bus import MessageBus, Message
from text import print_in_color

from workspace import DockerWorkspace


def handle_message(message):
    print_in_color(f"Received message from: {message.sender}", text.Color.GREEN)
    print_in_color(message.content, text.Color.GREEN)


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
        models=[
            "google/gemini-pro",
            "anthropic/claude-3-haiku:beta",
            "mistralai/mixtral-8x7b-instruct",
        ],
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
