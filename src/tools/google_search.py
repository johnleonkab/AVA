"""Herramienta de Google Search (ya integrada nativamente en Gemini)"""

from .base import BaseTool
from typing import List, Dict, Any
from google.genai import types


class GoogleSearchTool(BaseTool):
    """
    Herramienta para búsquedas en Google.
    Nota: Esta herramienta está integrada nativamente en Gemini,
    pero la mantenemos aquí para consistencia con el sistema de herramientas.
    """

    def get_function_declarations(self) -> List[types.FunctionDeclaration]:
        """Google Search está integrado nativamente, no necesita declaraciones"""
        return []

    async def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """No se ejecuta directamente, Gemini lo maneja internamente"""
        raise NotImplementedError(
            "Google Search es manejado nativamente por Gemini"
        )

