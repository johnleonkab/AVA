"""Configuración del agente y herramientas"""

import os
from google.genai import types

from ..tools import get_all_tools
from ..database import AssistantConfigDB


def _build_system_instruction() -> str:
    """
    Construye la instrucción del sistema basada en la configuración guardada
    
    Returns:
        Texto de la instrucción del sistema
    """
    db = AssistantConfigDB()
    config = db.get_config()
    
    # Mapeo de niveles
    sarcasm_level = config.get("sarcasm_level", 3)
    humor_level = config.get("humor_level", 5)
    response_length = config.get("response_length", "medium")
    formality = config.get("formality", "informal")
    treatment = config.get("treatment", "tú")
    
    # Construir descripción de sarcasmo
    if sarcasm_level == 0:
        sarcasm_desc = "No uses sarcasmo en absoluto."
    elif sarcasm_level <= 3:
        sarcasm_desc = "Usa sarcasmo ocasional y sutil."
    elif sarcasm_level <= 6:
        sarcasm_desc = "Usa sarcasmo moderado, de forma carismática."
    elif sarcasm_level <= 8:
        sarcasm_desc = "Usa bastante sarcasmo, siendo bastante vacilona."
    else:
        sarcasm_desc = "Usa mucho sarcasmo, siendo muy vacilona y mordaz."
    
    # Construir descripción de humor
    if humor_level == 0:
        humor_desc = "Mantén un tono serio y profesional."
    elif humor_level <= 3:
        humor_desc = "Usa humor ocasional y discreto."
    elif humor_level <= 6:
        humor_desc = "Usa humor moderado, siendo divertida y entretenida."
    elif humor_level <= 8:
        humor_desc = "Usa bastante humor, siendo muy divertida y ocurrente."
    else:
        humor_desc = "Usa mucho humor, siendo extremadamente divertida y chistosa."
    
    # Construir descripción de longitud
    length_desc = {
        "short": "Da respuestas cortas y concisas, ve directo al grano.",
        "medium": "Da respuestas de longitud media, equilibradas y completas.",
        "long": "Da respuestas detalladas y extensas, explicando bien todo."
    }.get(response_length, "Da respuestas de longitud media.")
    
    # Construir descripción de formalidad
    formality_desc = {
        "informal": "Usa un lenguaje informal y cercano, como entre amigos.",
        "formal": "Usa un lenguaje formal pero amigable, manteniendo respeto.",
        "very_formal": "Usa un lenguaje muy formal y respetuoso, como en contextos profesionales."
    }.get(formality, "Usa un lenguaje informal y cercano.")
    
    # Construir descripción de tratamiento
    treatment_desc = {
        "tú": f"Trátame de tú, de forma cercana.",
        "usted": f"Trátame de usted, de forma respetuosa.",
        "señor": f"Trátame como 'señor', de forma formal y respetuosa.",
        "señora": f"Trátame como 'señora', de forma formal y respetuosa."
    }.get(treatment, "Trátame de tú.")
    
    # Construir la instrucción completa
    instruction = (
        "Eres un asistente personal como el que tiene IronMan. "
        "Respondes en función de mis intereses, y de mi información personal. "
        "Vives en España, y por tanto conoces y presupones que conozco "
        "la cultura española y andaluza.\n\n"
        f"{sarcasm_desc}\n"
        f"{humor_desc}\n"
        f"{length_desc}\n"
        f"{formality_desc}\n"
        f"{treatment_desc}\n\n"
        "IMPORTANTE: Cuando termines de responder, debes callarte y esperar "
        "a que el usuario hable de nuevo. No continúes hablando indefinidamente."
    )
    
    return instruction


def get_live_config() -> types.LiveConnectConfig:
    """Obtiene la configuración para la conexión Live de Gemini"""
    tools = get_all_tools()
    system_instruction_text = _build_system_instruction()

    return types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        media_resolution="MEDIA_RESOLUTION_MEDIUM",
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Callirrhoe")
            )
        ),
        realtime_input_config=types.RealtimeInputConfig(
            turn_coverage=types.TurnCoverage.TURN_INCLUDES_ONLY_ACTIVITY
        ),
        context_window_compression=types.ContextWindowCompressionConfig(
            trigger_tokens=25600,
            sliding_window=types.SlidingWindow(target_tokens=12800),
        ),
        tools=tools,
        system_instruction=types.Content(
            parts=[
                types.Part.from_text(text=system_instruction_text)
            ],
            role="user",
        ),
    )

