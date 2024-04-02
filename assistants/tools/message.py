from assistants.tools.types import Tool
import message_bus


class Message(Tool):
    def __init__(self, message_bus: message_bus.MessageBus):
        self._message_bus = message_bus

    def function(self, content: str, recipient: str, caller: str) -> str:
        result = self._message_bus.publish(
            message_bus.Message(
                sender=caller,
                recipient=recipient,
                content=content,
            )
        )
        return "Message sent successfully" if result else "Failed sending message"
