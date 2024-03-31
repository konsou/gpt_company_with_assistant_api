import asyncio
from typing import Callable, Dict, List, Any


class Message:
    def __init__(self, sender: str, recipient: str, content: Any):
        self.sender = sender
        self.recipient = recipient
        self.content = content


class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Message], None]]] = {}

    async def publish(self, message: Message):
        if message.recipient in self.subscribers:
            for handler in self.subscribers[message.recipient]:
                await asyncio.create_task(handler(message))

    def subscribe(self, recipient: str, handler: Callable[[Message], None]):
        if recipient not in self.subscribers:
            self.subscribers[recipient] = []
        self.subscribers[recipient].append(handler)

    def unsubscribe(self, recipient: str, handler: Callable[[Message], None]):
        if recipient in self.subscribers:
            self.subscribers[recipient].remove(handler)
            if not self.subscribers[recipient]:
                del self.subscribers[recipient]
