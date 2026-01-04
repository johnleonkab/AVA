"""Loop principal de audio para streaming con Gemini"""

import asyncio
import base64
import io
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Optional

import cv2
import numpy as np
import pyaudio
import PIL.Image
import mss

from google import genai
from google.genai import types

from ..agent.config import get_live_config
from ..tools.assistant_config import AssistantConfigTool
from .audio_handler import AudioHandler, SEND_SAMPLE_RATE, CHUNK_SIZE, RECEIVE_SAMPLE_RATE
from .echo_cancellation import AudioProcessor

DEFAULT_MODE = "camera"

# Colores para la consola (ANSI)
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RED = '\033[91m'


class AudioLoop:
    """Maneja el loop principal de audio y streaming"""

    def __init__(self, video_mode: str = DEFAULT_MODE):
        self.video_mode = video_mode
        self.audio_in_queue: Optional[asyncio.Queue] = None
        self.out_queue: Optional[asyncio.Queue] = None
        self.session = None
        self.pya = pyaudio.PyAudio()
        self.audio_handler = AudioHandler(self.pya)
        
        # Procesador de audio para echo cancellation
        self.audio_processor = AudioProcessor(
            sample_rate=SEND_SAMPLE_RATE,
            buffer_size=CHUNK_SIZE
        )
        
        # Herramientas para function calling
        self.assistant_config_tool = AssistantConfigTool()
        
        # Contadores para estadísticas
        self.audio_chunks_sent = 0
        self.audio_chunks_received = 0
        self.frames_sent = 0
        self.last_activity_time = None
        self.is_speaking = False
        self.is_listening = False

    def _log(self, message: str, color: str = Colors.RESET, prefix: str = "INFO"):
        """Imprime un mensaje con timestamp y color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {prefix}: {message}{Colors.RESET}", flush=True)

    def _log_mic(self, message: str):
        """Log específico para micrófono"""
        self._log(message, Colors.CYAN, "MIC")

    def _log_assistant(self, message: str):
        """Log específico para el asistente"""
        self._log(message, Colors.MAGENTA, "ASST")

    def _log_system(self, message: str):
        """Log específico para el sistema"""
        self._log(message, Colors.BLUE, "SYS")

    def _log_error(self, message: str):
        """Log específico para errores"""
        self._log(message, Colors.RED, "ERROR")

    def _log_success(self, message: str):
        """Log específico para éxito"""
        self._log(message, Colors.GREEN, "OK")

    async def send_text(self):
        """Envía texto como input al modelo"""
        self._log_system("Modo texto activado. Escribe 'q' para salir.")
        while True:
            text = await asyncio.to_thread(input, f"{Colors.YELLOW}message > {Colors.RESET}")
            if text.lower() == "q":
                self._log_system("Saliendo...")
                break
            if text.strip():
                self._log(f"Enviando texto: {text}", Colors.YELLOW, "TEXT")
                await self.session.send(input=text or ".", end_of_turn=True)

    def _get_frame(self, cap):
        """Obtiene un frame de la cámara"""
        ret, frame = cap.read()
        if not ret:
            return None
        # Convertir BGR a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)
        img.thumbnail([1024, 1024])

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        """Obtiene frames de la cámara de forma asíncrona"""
        cap = await asyncio.to_thread(cv2.VideoCapture, 0)

        while True:
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break

            await asyncio.sleep(1.0)
            await self.out_queue.put(frame)

        cap.release()

    def _get_screen(self):
        """Captura la pantalla"""
        sct = mss.mss()
        monitor = sct.monitors[0]
        i = sct.grab(monitor)

        mime_type = "image/jpeg"
        image_bytes = mss.tools.to_png(i.rgb, i.size)
        img = PIL.Image.open(io.BytesIO(image_bytes))

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_screen(self):
        """Captura la pantalla de forma asíncrona"""
        while True:
            frame = await asyncio.to_thread(self._get_screen)
            if frame is None:
                break

            await asyncio.sleep(1.0)
            await self.out_queue.put(frame)

    async def send_realtime(self):
        """Envía datos en tiempo real (video/frames)"""
        while True:
            msg = await self.out_queue.get()
            # Detectar si es audio o video
            if isinstance(msg, dict):
                if msg.get("mime_type") == "audio/pcm":
                    # Es audio, no lo logueamos para no saturar
                    pass
                elif msg.get("mime_type") == "image/jpeg":
                    # Es un frame de video
                    self.frames_sent += 1
                    if self.frames_sent % 10 == 0:  # Log cada 10 frames
                        self._log(f"Frame de video enviado (total: {self.frames_sent})", Colors.BLUE, "VIDEO")
            await self.session.send(input=msg)

    async def listen_audio(self):
        """Escucha audio del micrófono (echo cancellation desactivado temporalmente)"""
        self._log_mic("Iniciando captura de audio del micrófono...")
        await self.audio_handler.open_input_stream()
        self._log_success("Micrófono listo y capturando audio")
        self._log_system("⚠️  Echo cancellation DESACTIVADO temporalmente para debugging")
        self.is_listening = True
        
        last_log_time = time.time()
        
        while True:
            data = await self.audio_handler.read_audio_chunk()
            current_time = time.time()
            
            # Enviar audio directamente sin procesamiento (para debugging)
            # TODO: Reactivar echo cancellation cuando funcione correctamente
            self.audio_chunks_sent += 1
            self.last_activity_time = current_time
            
            await self.out_queue.put(data)
            
            # Log cada segundo aproximadamente
            if current_time - last_log_time >= 1.0:
                self._log_mic(f"Audio capturado ({self.audio_chunks_sent} chunks enviados)")
                last_log_time = current_time

    async def receive_audio(self):
        """Recibe audio del websocket y lo pone en la cola"""
        self._log_assistant("Esperando respuesta del asistente...")
        while True:
            turn = self.session.receive()
            interrupted = False
            turn_started = False
            text_buffer = []
            last_audio_time = None
            
            async for response in turn:
                # Detectar si el turno fue interrumpido
                if hasattr(response, 'interrupted') and response.interrupted:
                    interrupted = True
                    self._log_error("⚠️  Turno interrumpido por el usuario")
                elif hasattr(response, 'turn_complete'):
                    if hasattr(response.turn_complete, 'interrupted'):
                        interrupted = response.turn_complete.interrupted
                        if interrupted:
                            self._log_error("⚠️  Turno interrumpido")
                    # turn_complete indica que el turno terminó normalmente
                    if not interrupted:
                        self._log_assistant("✅ Turno completado por el modelo")
                
                # Procesar audio PRIMERO (prioridad máxima - no bloquear nunca)
                if data := response.data:
                    if not turn_started:
                        turn_started = True
                        self.is_speaking = True
                        self._log_assistant("🎤 Asistente empezando a hablar...")
                    
                    last_audio_time = time.time()
                    self.audio_chunks_received += 1
                    self.audio_in_queue.put_nowait(data)
                    continue
                
                # Procesar texto
                if text := response.text:
                    text_buffer.append(text)
                    # Mostrar texto en tiempo real
                    print(f"{Colors.MAGENTA}{text}{Colors.RESET}", end="", flush=True)
                
                # Manejar function calling SOLO si no hay audio/texto (no bloquear)
                # Ejecutar en background para no interrumpir el flujo
                if hasattr(response, 'function_call') and response.function_call:
                    asyncio.create_task(self._handle_function_call(response.function_call))
                elif hasattr(response, 'function_calls') and response.function_calls:
                    for fc in response.function_calls:
                        asyncio.create_task(self._handle_function_call(fc))
            
            # Al finalizar el turno, marcar que el asistente ya no está hablando
            if turn_started:
                self.is_speaking = False
                full_text = "".join(text_buffer)
                if full_text.strip():
                    self._log_assistant(f"✅ Asistente terminó de hablar - Esperando tu respuesta...")
                else:
                    self._log_assistant("✅ Asistente terminó de hablar - Esperando tu respuesta...")
            
            # Reseteo de seguridad: si no hay audio recibido en los últimos 3 segundos, resetear flag
            if self.is_speaking and last_audio_time:
                time_since_last_audio = time.time() - last_audio_time
                if time_since_last_audio > 3.0:
                    self._log_system("⚠️  Reseteando is_speaking (timeout - no hay audio desde hace 3s)")
                    self.is_speaking = False
            
            # Solo vaciar la cola si hubo una interrupción real del usuario
            if interrupted:
                self._log_error("🗑️  Limpiando cola de audio debido a interrupción")
                while not self.audio_in_queue.empty():
                    try:
                        self.audio_in_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break

    async def _handle_function_call(self, function_call):
        """
        Maneja las llamadas a funciones del modelo (ejecuta en background)
        
        Args:
            function_call: Objeto con la información de la función a ejecutar
        """
        try:
            # Extraer nombre y argumentos
            function_name = None
            arguments = {}
            
            if hasattr(function_call, 'name'):
                function_name = function_call.name
            elif hasattr(function_call, 'function_call') and hasattr(function_call.function_call, 'name'):
                function_name = function_call.function_call.name
            
            if hasattr(function_call, 'args'):
                args_val = function_call.args
                if args_val:
                    arguments = dict(args_val) if isinstance(args_val, dict) else {}
            elif hasattr(function_call, 'function_call') and hasattr(function_call.function_call, 'args'):
                args_val = function_call.function_call.args
                if args_val:
                    arguments = dict(args_val) if isinstance(args_val, dict) else {}
            
            if not function_name:
                return
            
            self._log_system(f"🔧 Ejecutando función: {function_name}")
            
            # Ejecutar la función
            if function_name.startswith("set_") or function_name.startswith("get_") or function_name == "reset_assistant_config":
                result = await self.assistant_config_tool.execute(function_name, arguments)
                self._log_success(f"✅ {result.get('message', 'Función ejecutada')}")
                
                # Enviar resultado de vuelta al modelo
                if self.session:
                    try:
                        function_response = types.Part.from_function_response(
                            name=function_name,
                            response=result
                        )
                        await self.session.send(
                            input=types.Content(
                                parts=[function_response],
                                role="tool"
                            )
                        )
                    except Exception as e:
                        self._log_error(f"Error enviando resultado: {e}")
        except Exception as e:
            self._log_error(f"Error en function call: {e}")
    
    async def play_audio(self):
        """Reproduce audio desde la cola y lo envía al procesador de eco"""
        self._log_system("Iniciando reproducción de audio...")
        stream = await self.audio_handler.open_output_stream()
        self._log_success("Altavoces listos")
        
        while True:
            bytestream = await self.audio_in_queue.get()
            
            # Enviar audio de salida al procesador para echo cancellation
            self.audio_processor.process_output(bytestream)
            
            # Reproducir audio
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        """Ejecuta el loop principal"""
        self._log_system("=" * 60)
        self._log_system("Iniciando Asistente Virtual con Gemini")
        self._log_system("=" * 60)
        
        try:
            self._log_system("Cargando configuración...")
            config = get_live_config()
            self._log_success("Configuración cargada")
            
            self._log_system("Conectando con Gemini API...")
            client = genai.Client(
                http_options={"api_version": "v1beta"},
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            async with (
                client.aio.live.connect(model="models/gemini-2.5-flash-native-audio-preview-12-2025", config=config) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self._log_success("✅ Conectado con Gemini Live API")

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                self._log_system("Iniciando tareas...")
                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())

                if self.video_mode == "camera":
                    self._log_system("Modo: Cámara activada")
                    tg.create_task(self.get_frames())
                elif self.video_mode == "screen":
                    self._log_system("Modo: Captura de pantalla activada")
                    tg.create_task(self.get_screen())
                else:
                    self._log_system("Modo: Solo audio (sin video)")

                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                self._log_success("🚀 Sistema completamente inicializado y listo")
                self._log_system("-" * 60)
                
                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            self._log_system("Cerrando conexión...")
        except Exception as e:
            self._log_error(f"Error inesperado: {e}")
            self.audio_handler.close_input_stream()
            traceback.print_exc()
        finally:
            self._log_system("Limpiando recursos...")
            self.pya.terminate()
            self._log_success("Sistema cerrado correctamente")

