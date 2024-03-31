from assistants.open_ai import OpenAIAssistant
from assistants.open_router import OpenRouterAssistant
from message_bus import MessageBus, Message

from workspace.dummy import DummyWorkspace


def handle_message(message):
    print(f"Received message from: {message.sender}")
    print(message.content)


def main():
    message_bus = MessageBus()
    workspace = DummyWorkspace()

    ass = OpenRouterAssistant(
        model="databricks/dbrx-instruct",
        name="Erkki",
        role="Software Developer",
        instructions="You write code that fulfills the customer's requests. You can execute commands in your dev environment by enclosing them in <execute></execute> tags.",
        message_bus=message_bus,
        workspace=workspace,
    )
    message_bus.subscribe("konso", handle_message)
    message_bus.publish(
        Message(
            sender="konso",
            recipient="Erkki",
            content="Please check your dev env directory contents",
        )
    )


if __name__ == "__main__":
    main()
