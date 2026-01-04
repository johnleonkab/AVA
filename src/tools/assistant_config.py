"""Herramienta para gestionar la configuración del asistente (meta órdenes)"""

from .base import BaseTool
from typing import List, Dict, Any
from google.genai import types

from ..database import AssistantConfigDB


class AssistantConfigTool(BaseTool):
    """
    Herramienta para gestionar la configuración del asistente:
    - Nivel de sarcasmo
    - Nivel de humor
    - Longitud de respuestas
    - Formalidad y tratamiento
    """
    
    def __init__(self):
        """Inicializa la herramienta de configuración"""
        self.db = AssistantConfigDB()
    
    def get_function_declarations(self) -> List[types.FunctionDeclaration]:
        """
        Retorna las declaraciones de funciones para gestión de configuración
        
        Returns:
            Lista de FunctionDeclaration
        """
        return [
            self._create_function_declaration(
                name="set_sarcasm_level",
                description=(
                    "Establece el nivel de sarcasmo del asistente (0-10). "
                    "0 = sin sarcasmo, 10 = muy sarcástico"
                ),
                parameters={
                    "level": {
                        "type": "integer",
                        "description": "Nivel de sarcasmo de 0 a 10",
                        "minimum": 0,
                        "maximum": 10
                    }
                }
            ),
            self._create_function_declaration(
                name="set_humor_level",
                description=(
                    "Establece el nivel de humor del asistente (0-10). "
                    "0 = serio, 10 = muy divertido"
                ),
                parameters={
                    "level": {
                        "type": "integer",
                        "description": "Nivel de humor de 0 a 10",
                        "minimum": 0,
                        "maximum": 10
                    }
                }
            ),
            self._create_function_declaration(
                name="set_response_length",
                description=(
                    "Establece la longitud preferida de las respuestas del asistente"
                ),
                parameters={
                    "length": {
                        "type": "string",
                        "description": "Longitud de respuesta: 'short' (corta), 'medium' (media), 'long' (larga)",
                        "enum": ["short", "medium", "long"]
                    }
                }
            ),
            self._create_function_declaration(
                name="set_formality",
                description=(
                    "Establece el nivel de formalidad del asistente"
                ),
                parameters={
                    "formality": {
                        "type": "string",
                        "description": "Nivel de formalidad: 'informal' (informal), 'formal' (formal), 'very_formal' (muy formal)",
                        "enum": ["informal", "formal", "very_formal"]
                    }
                }
            ),
            self._create_function_declaration(
                name="set_treatment",
                description=(
                    "Establece cómo debe tratarte el asistente"
                ),
                parameters={
                    "treatment": {
                        "type": "string",
                        "description": "Forma de tratamiento: 'tú' (tuteo), 'usted' (usted), 'señor' (señor), 'señora' (señora)",
                        "enum": ["tú", "usted", "señor", "señora"]
                    }
                }
            ),
            self._create_function_declaration(
                name="get_assistant_config",
                description=(
                    "Obtiene la configuración actual del asistente. "
                    "Útil para saber qué ajustes tiene actualmente"
                ),
                parameters={}
            ),
            self._create_function_declaration(
                name="reset_assistant_config",
                description=(
                    "Restablece la configuración del asistente a los valores por defecto"
                ),
                parameters={}
            ),
        ]
    
    async def execute(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Ejecuta una función de configuración
        
        Args:
            function_name: Nombre de la función a ejecutar
            arguments: Argumentos de la función
            
        Returns:
            Resultado de la ejecución
        """
        if function_name == "set_sarcasm_level":
            level = arguments.get("level")
            if level is None or not (0 <= level <= 10):
                return {"error": "El nivel de sarcasmo debe estar entre 0 y 10"}
            self.db.set("sarcasm_level", level)
            return {
                "success": True,
                "message": f"Nivel de sarcasmo establecido a {level}/10",
                "sarcasm_level": level
            }
        
        elif function_name == "set_humor_level":
            level = arguments.get("level")
            if level is None or not (0 <= level <= 10):
                return {"error": "El nivel de humor debe estar entre 0 y 10"}
            self.db.set("humor_level", level)
            return {
                "success": True,
                "message": f"Nivel de humor establecido a {level}/10",
                "humor_level": level
            }
        
        elif function_name == "set_response_length":
            length = arguments.get("length")
            if length not in ["short", "medium", "long"]:
                return {"error": "La longitud debe ser 'short', 'medium' o 'long'"}
            self.db.set("response_length", length)
            length_es = {"short": "corta", "medium": "media", "long": "larga"}[length]
            return {
                "success": True,
                "message": f"Longitud de respuesta establecida a {length_es}",
                "response_length": length
            }
        
        elif function_name == "set_formality":
            formality = arguments.get("formality")
            if formality not in ["informal", "formal", "very_formal"]:
                return {"error": "La formalidad debe ser 'informal', 'formal' o 'very_formal'"}
            self.db.set("formality", formality)
            formality_es = {
                "informal": "informal",
                "formal": "formal",
                "very_formal": "muy formal"
            }[formality]
            return {
                "success": True,
                "message": f"Formalidad establecida a {formality_es}",
                "formality": formality
            }
        
        elif function_name == "set_treatment":
            treatment = arguments.get("treatment")
            if treatment not in ["tú", "usted", "señor", "señora"]:
                return {"error": "El tratamiento debe ser 'tú', 'usted', 'señor' o 'señora'"}
            self.db.set("treatment", treatment)
            return {
                "success": True,
                "message": f"Tratamiento establecido a '{treatment}'",
                "treatment": treatment
            }
        
        elif function_name == "get_assistant_config":
            config = self.db.get_config()
            return {
                "success": True,
                "config": config,
                "message": "Configuración actual del asistente obtenida"
            }
        
        elif function_name == "reset_assistant_config":
            self.db.reset_to_defaults()
            return {
                "success": True,
                "message": "Configuración restablecida a valores por defecto",
                "config": self.db.get_config()
            }
        
        else:
            raise ValueError(f"Función {function_name} no encontrada en AssistantConfigTool")

