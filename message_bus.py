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

    def publish(self, message: Message) -> bool:
        recipient = message.recipient.lower()
        if recipient in self.subscribers:
            for handler in self.subscribers[recipient]:
                handler(message)
                return True
        return False

    def subscribe(self, recipient: str, handler: Callable[[Message], None]):
        recipient = recipient.lower()
        if recipient not in self.subscribers:
            self.subscribers[recipient] = []
        self.subscribers[recipient].append(handler)
        print(f"{recipient} subscribed to message bus")

    def unsubscribe(self, recipient: str, handler: Callable[[Message], None]):
        recipient = recipient.lower()
        if recipient in self.subscribers:
            self.subscribers[recipient].remove(handler)
            if not self.subscribers[recipient]:
                del self.subscribers[recipient]
        print(f"{recipient} unsubscribed from message bus")
