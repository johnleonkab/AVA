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

    # Google Search (funciona nativamente con Gemini Live)
    tools.append(types.Tool(google_search=types.GoogleSearch()))

    # NOTA: Function calling está DESACTIVADO temporalmente
    # El function calling en Gemini Live API rompe el flujo de audio
    # cuando se ejecuta una función. El modelo se queda esperando
    # la respuesta y no continúa con el audio.
    # 
    # TODO: Investigar cómo implementar function calling correctamente
    # en Gemini Live API sin romper el flujo de audio.
    #
    # Para habilitar function calling, descomentar el siguiente código:
    #
    # function_declarations = []
    # assistant_config_tool = AssistantConfigTool()
    # function_declarations.extend(assistant_config_tool.get_function_declarations())
    # if function_declarations:
    #     tools.append(types.Tool(function_declarations=function_declarations))

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

