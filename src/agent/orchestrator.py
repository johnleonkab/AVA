"""Agente orquestador principal"""

import os
from typing import Optional
from google import genai


class Orchestrator:
    """Agente principal que orquesta las interacciones con Gemini"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el orquestador

        Args:
            api_key: API key de Gemini. Si no se proporciona, se usa la variable de entorno
        """
        self.client = genai.Client(
            http_options={"api_version": "v1beta"},
            api_key=api_key or os.environ.get("GEMINI_API_KEY"),
        )
        self.model = "models/gemini-2.5-flash-native-audio-preview-12-2025"

    def get_client(self):
        """Obtiene el cliente de Gemini"""
        return self.client

