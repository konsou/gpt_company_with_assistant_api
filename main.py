import asyncio
import time

from assistants.open_ai import OpenAIAssistant
from message_bus import MessageBus, Message


def handle_message(message):
    print(f"Received message from: {message.sender}")
    print(message.content)


def main():
    message_bus = MessageBus()

    ass = OpenAIAssistant(
        model="gpt-4-0125-preview",
        name="Erkki",
        role="Software Developer",
        instructions="You write code that fulfills the customer's requests",
        message_bus=message_bus,
    )
    message_bus.subscribe("konso", handle_message)
    message_bus.publish(
        Message(
            sender="konso",
            recipient="Erkki",
            content="What is the capital of Mongolia?",
        )
    )


if __name__ == "__main__":
    main()
