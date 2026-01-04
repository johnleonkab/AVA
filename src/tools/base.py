"""Clase base para herramientas"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from google.genai import types


class BaseTool(ABC):
    """Clase base abstracta para todas las herramientas"""

    @abstractmethod
    def get_function_declarations(self) -> List[types.FunctionDeclaration]:
        """
        Retorna las declaraciones de funciones para Gemini

        Returns:
            Lista de FunctionDeclaration
        """
        pass

    @abstractmethod
    async def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Ejecuta una función de la herramienta

        Args:
            function_name: Nombre de la función a ejecutar
            arguments: Argumentos de la función

        Returns:
            Resultado de la ejecución
        """
        pass

    def _create_function_declaration(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
    ) -> types.FunctionDeclaration:
        """
        Crea una declaración de función para Gemini

        Args:
            name: Nombre de la función
            description: Descripción de la función
            parameters: Esquema de parámetros (JSON Schema)

        Returns:
            FunctionDeclaration configurada
        """
        return types.FunctionDeclaration(
            name=name,
            description=description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties=parameters,
            ),
        )

