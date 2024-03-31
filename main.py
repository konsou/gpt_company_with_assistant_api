import asyncio

from assistants.open_ai import OpenAIAssistant
from message_bus import MessageBus, Message


async def handle_message(message):
    print(f"Received message from: {message.sender}")
    print(message.content)


async def main():
    message_bus = MessageBus()

    ass = OpenAIAssistant(
        model="gpt-4-0125-preview",
        name="Erkki",
        instructions="You answer the user's questions in haiku form",
        message_bus=message_bus,
    )
    message_bus.subscribe("konso", handle_message)
    await message_bus.publish(
        Message(
            sender="konso",
            recipient="Erkki",
            content="What is the capital of Mongolia?",
        )
    )
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
