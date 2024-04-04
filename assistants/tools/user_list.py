from assistants.tools.abc import Tool
import message_bus


class UserList(Tool):
    def __init__(self, message_bus: message_bus.MessageBus):
        self._message_bus = message_bus

    def function(self, caller: str, *args, **kwargs) -> str:
        return ", ".join(self._message_bus.subscribers.keys())
