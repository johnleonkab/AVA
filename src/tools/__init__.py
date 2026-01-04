"""Sistema de herramientas para function calling"""

from .base import BaseTool
from .google_search import GoogleSearchTool
from .google_suite import GoogleSuiteTool
from .file_manager import FileManagerTool
from .shopping_list import ShoppingListTool
from .assistant_config import AssistantConfigTool

from google.genai import types


def get_all_tools() -> list:
    """
    Obtiene todas las herramientas disponibles para Gemini

    Returns:
        Lista de herramientas configuradas para Gemini
    """
    tools = []

    # Google Search (ya implementado)
    tools.append(types.Tool(google_search=types.GoogleSearch()))

    # Function calling tools
    function_declarations = []

    # Assistant Config (meta órdenes) - IMPLEMENTADO
    assistant_config_tool = AssistantConfigTool()
    function_declarations.extend(assistant_config_tool.get_function_declarations())

    # Google Suite (preparado para futuro)
    google_suite_tool = GoogleSuiteTool()
    function_declarations.extend(google_suite_tool.get_function_declarations())

    # File Manager (preparado para futuro)
    file_manager_tool = FileManagerTool()
    function_declarations.extend(file_manager_tool.get_function_declarations())

    # Shopping List (preparado para futuro)
    shopping_list_tool = ShoppingListTool()
    function_declarations.extend(shopping_list_tool.get_function_declarations())

    if function_declarations:
        tools.append(types.Tool(function_declarations=function_declarations))

    return tools


__all__ = [
    "BaseTool",
    "GoogleSearchTool",
    "GoogleSuiteTool",
    "FileManagerTool",
    "ShoppingListTool",
    "AssistantConfigTool",
    "get_all_tools",
]

