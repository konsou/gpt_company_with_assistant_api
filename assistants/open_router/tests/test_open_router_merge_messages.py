import os
from unittest import TestCase

from assistants.base import InternalMessage
from ._open_router_assistant_factory import open_router_assistant_factory

USER_MESSAGE: InternalMessage = {
    "role": "user",
    "content": f"Hello Test",
}
TOOL_MESSAGE: InternalMessage = {
    "role": "tool",
    "content": f"Hello Tool",
}
ASSISTANT_MESSAGE: InternalMessage = {
    "role": "assistant",
    "content": f"Hello Assistant",
}


class TestOpenRouterAssistant(TestCase):
    def setUp(self):
        os.environ["OPENROUTER_API_KEY"] = "test-key"

    def test_merge_user_messages(self):
        ora = open_router_assistant_factory()
        ora._messages = [USER_MESSAGE]
        ora._merge_or_add_message(USER_MESSAGE)
        self.assertEqual(
            [
                {
                    "role": "user",
                    "content": f"User: {USER_MESSAGE['content']}\nUser: {USER_MESSAGE['content']}",
                }
            ],
            ora._messages,
        )

    def test_merge_tool_messages(self):
        ora = open_router_assistant_factory()
        ora._messages = [TOOL_MESSAGE]
        ora._merge_or_add_message(TOOL_MESSAGE)
        self.assertEqual(
            [
                {
                    "role": "user",
                    "content": f"Tool: {TOOL_MESSAGE['content']}\nTool: {TOOL_MESSAGE['content']}",
                }
            ],
            ora._messages,
        )

    def test_merge_tool_user_messages(self):
        ora = open_router_assistant_factory()
        ora._messages = [TOOL_MESSAGE]
        ora._merge_or_add_message(USER_MESSAGE)
        self.assertEqual(
            [
                {
                    "role": "user",
                    "content": f"Tool: {TOOL_MESSAGE['content']}\nUser: {USER_MESSAGE['content']}",
                }
            ],
            ora._messages,
        )

    def test_merge_user_tool_messages(self):
        ora = open_router_assistant_factory()
        ora._messages = [USER_MESSAGE]
        ora._merge_or_add_message(TOOL_MESSAGE)
        self.assertEqual(
            [
                {
                    "role": "user",
                    "content": f"User: {USER_MESSAGE['content']}\nTool: {TOOL_MESSAGE['content']}",
                }
            ],
            ora._messages,
        )

    def test_dont_merge_assistant_messages(self):
        ora = open_router_assistant_factory()
        ora._messages = [ASSISTANT_MESSAGE]
        ora._merge_or_add_message(ASSISTANT_MESSAGE)
        self.assertEqual(
            [ASSISTANT_MESSAGE, ASSISTANT_MESSAGE],
            ora._messages,
        )
