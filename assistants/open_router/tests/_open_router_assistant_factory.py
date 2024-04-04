from unittest.mock import MagicMock, create_autospec

from assistants.open_router import OpenRouterAssistant
from workspace import Workspace


def open_router_assistant_factory() -> OpenRouterAssistant:
    ora = OpenRouterAssistant(
        instructions="",
        message_bus=MagicMock(),
        name="",
        role="",
        workspace=create_autospec(Workspace),
        models=["model1", "model2"],
    )
    return ora
