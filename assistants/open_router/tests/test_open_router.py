import os
from unittest import TestCase
from unittest.mock import MagicMock, create_autospec

from assistants.open_router import OpenRouterAssistant
from workspace import Workspace


class TestOpenRouterAssistant(TestCase):
    def setUp(self):
        os.environ["OPENROUTER_API_KEY"] = "test-key"

    def test_select_override_model_one_model(self):
        ora = OpenRouterAssistant(
            instructions="",
            message_bus=MagicMock(),
            name="",
            role="",
            workspace=create_autospec(Workspace),
            model="one_model",
        )
        ora.empty_message_limit = 3
        ora._empty_messages_by_model["one_model"] = 4
        with self.assertRaises(RuntimeError):
            ora.select_override_model()

    def test_select_override_model_one_model_list(self):
        ora = OpenRouterAssistant(
            instructions="",
            message_bus=MagicMock(),
            name="",
            role="",
            workspace=create_autospec(Workspace),
            models=["one_model"],
        )

        ora.empty_message_limit = 3
        ora._empty_messages_by_model["one_model"] = 4
        with self.assertRaises(RuntimeError):
            ora.select_override_model()

    def test_no_select_override_model_one_model(self):
        ora = OpenRouterAssistant(
            instructions="",
            message_bus=MagicMock(),
            name="",
            role="",
            workspace=create_autospec(Workspace),
            model="one_model",
        )
        ora.empty_message_limit = 3
        ora._empty_messages_by_model["one_model"] = 3
        result = ora.select_override_model()
        self.assertIsNone(result)

    def test_no_select_override_model_one_model_list(self):
        ora = OpenRouterAssistant(
            instructions="",
            message_bus=MagicMock(),
            name="",
            role="",
            workspace=create_autospec(Workspace),
            models=["one_model"],
        )
        ora.empty_message_limit = 3
        ora._empty_messages_by_model["one_model"] = 3
        result = ora.select_override_model()
        self.assertIsNone(result)

    def test_select_override_model_two_models(self):
        ora = OpenRouterAssistant(
            instructions="",
            message_bus=MagicMock(),
            name="",
            role="",
            workspace=create_autospec(Workspace),
            models=["model1", "model2"],
        )
        ora.empty_message_limit = 3
        ora._empty_messages_by_model["model1"] = 4
        result = ora.select_override_model()
        self.assertEqual("model2", result)

    def test_no_select_override_model_two_models(self):
        ora = OpenRouterAssistant(
            instructions="",
            message_bus=MagicMock(),
            name="",
            role="",
            workspace=create_autospec(Workspace),
            models=["model1", "model2"],
        )
        ora.empty_message_limit = 3
        ora._empty_messages_by_model["model1"] = 3
        result = ora.select_override_model()
        self.assertIsNone(result)

    def test_empty_message_counter_decremented(self):
        ora = OpenRouterAssistant(
            instructions="",
            message_bus=MagicMock(),
            name="",
            role="",
            workspace=create_autospec(Workspace),
            models=["model1", "model2"],
        )
        ora.empty_message_limit = 3
        ora._empty_messages_by_model["model1"] = 4
        ora.select_override_model()
        self.assertEqual(3, ora._empty_messages_by_model["model1"])
