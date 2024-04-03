from assistants.open_ai import OpenAIAssistant
from assistants.open_router import OpenRouterAssistant
from instructions import DEVELOPER_INSTRUCTIONS
from message_bus import MessageBus, Message

from workspace import DockerWorkspace


def handle_message(message):
    print(f"Received message from: {message.sender}")
    print(message.content)


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
    send_message(
        content="Please implement a console-based tic-tac-toe game in python. Save the code in your dev env. Let me know when you're finished and I'll check it out.",
        message_bus=message_bus,
    )
    while True:
        ass.process_messages()
        s = input("konso: ")
        if s.strip():
            send_message(content=s, message_bus=message_bus)


# TODO: shell commands wonky

if __name__ == "__main__":
    main()
