from assistants.open_ai import OpenAIAssistant
from assistants.open_router import OpenRouterAssistant
from message_bus import MessageBus, Message

from workspace import Workspace


def handle_message(message):
    print(f"Received message from: {message.sender}")
    print(message.content)


def main():
    message_bus = MessageBus()
    workspace = Workspace()

    ass = OpenRouterAssistant(
        model="databricks/dbrx-instruct",
        name="Erkki",
        role="Software Developer",
        instructions="You write code that fulfills the customer's requests but ALWAYS INCLUDE EMOJIS in the code",
        message_bus=message_bus,
        workspace=workspace,
    )
    message_bus.subscribe("konso", handle_message)
    message_bus.publish(
        Message(
            sender="konso",
            recipient="Erkki",
            content="Write a python program for displaying numbers 1..100",
        )
    )


if __name__ == "__main__":
    main()
