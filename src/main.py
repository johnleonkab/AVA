"""Punto de entrada principal del asistente virtual"""

import argparse
import asyncio
import os
import sys

from src.audio import AudioLoop

DEFAULT_MODE = "camera"


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Asistente Virtual con IA - Orquestado por Gemini"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default=DEFAULT_MODE,
        help="Modo de video: camera, screen, o none",
        choices=["camera", "screen", "none"],
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key de Gemini (opcional, usa GEMINI_API_KEY por defecto)",
    )

    args = parser.parse_args()

    # Verificar API key
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "Error: GEMINI_API_KEY no encontrada. "
            "Establece la variable de entorno o usa --api-key"
        )
        sys.exit(1)

    # Establecer API key si se proporcionó como argumento
    if args.api_key:
        os.environ["GEMINI_API_KEY"] = args.api_key

    # Crear y ejecutar el loop de audio
    audio_loop = AudioLoop(video_mode=args.mode)
    asyncio.run(audio_loop.run())


if __name__ == "__main__":
    main()

