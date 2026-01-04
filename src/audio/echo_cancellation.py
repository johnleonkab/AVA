"""Echo cancellation y Voice Activity Detection usando librerías robustas"""

import numpy as np
from typing import Tuple, Optional
import collections

# Intentar importar webrtcvad
try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    print("⚠️  webrtcvad no disponible, usando detección básica de voz")

# Intentar importar speexdsp (opcional, requiere SWIG)
try:
    from speexdsp import EchoCanceller as SpeexEchoCanceller
    SPEEXDSP_AVAILABLE = True
except ImportError:
    SPEEXDSP_AVAILABLE = False


class SimpleEchoCanceller:
    """
    Cancelador de eco simple usando correlación cruzada y atenuación.
    Funciona sin dependencias externas complejas.
    """
    
    def __init__(self, sample_rate: int = 16000, buffer_size: int = 1024):
        """
        Inicializa el cancelador de eco
        
        Args:
            sample_rate: Frecuencia de muestreo
            buffer_size: Tamaño del buffer
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        # Buffer circular para el audio de salida (lo que reproduce el asistente)
        # Guardamos hasta 0.5 segundos de audio de salida
        buffer_length = int(sample_rate * 0.5)
        self.output_buffer = collections.deque(maxlen=buffer_length)
        
        # Factor de atenuación para el eco
        self.attenuation_factor = 0.8
        
    def add_output_audio(self, audio_data: bytes) -> None:
        """
        Añade audio de salida al buffer (lo que está reproduciendo el asistente)
        
        Args:
            audio_data: Audio de salida en bytes (int16)
        """
        # Convertir bytes a numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Añadir al buffer circular
        self.output_buffer.extend(audio_array)
    
    def process_input(self, input_audio: bytes) -> bytes:
        """
        Procesa el audio de entrada eliminando el eco
        
        Args:
            input_audio: Audio del micrófono en bytes
            
        Returns:
            Audio procesado sin eco en bytes
        """
        if len(self.output_buffer) == 0:
            # No hay audio de salida, devolver entrada sin procesar
            return input_audio
        
        # Convertir bytes a numpy array
        input_array = np.frombuffer(input_audio, dtype=np.int16)
        
        # Convertir a float32 para procesamiento
        input_float = input_array.astype(np.float32) / 32768.0
        
        # Obtener el audio de salida más reciente (mismo tamaño que entrada)
        output_list = list(self.output_buffer)
        if len(output_list) < len(input_array):
            # No hay suficiente audio de salida, solo atenuar
            processed = input_float * 0.5
        else:
            # Obtener la parte más reciente del buffer
            output_array = np.array(output_list[-len(input_array):], dtype=np.float32) / 32768.0
            
            # Calcular correlación cruzada para encontrar el delay
            correlation = np.correlate(np.abs(input_float), np.abs(output_array), mode='valid')
            
            if len(correlation) > 0:
                # Encontrar el delay máximo
                delay = np.argmax(correlation)
                
                # Ajustar el audio de salida según el delay
                if delay < len(output_array):
                    aligned_output = output_array[delay:delay+len(input_float)]
                    if len(aligned_output) == len(input_float):
                        # Restar el eco (con atenuación)
                        processed = input_float - (aligned_output * self.attenuation_factor)
                    else:
                        processed = input_float * 0.7
                else:
                    processed = input_float * 0.7
            else:
                processed = input_float * 0.7
        
        # Limitar valores y convertir de vuelta a int16
        processed = np.clip(processed, -1.0, 1.0)
        processed = (processed * 32767.0).astype(np.int16)
        
        return processed.tobytes()


class RobustEchoCanceller:
    """
    Cancelador de eco robusto usando SpeexDSP (si está disponible) o método simple
    """
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        """
        Inicializa el cancelador de eco
        
        Args:
            sample_rate: Frecuencia de muestreo (16kHz para entrada)
            chunk_size: Tamaño del chunk de audio
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # WebRTC VAD para detectar voz del usuario
        if WEBRTCVAD_AVAILABLE:
            # Mode: 0=quality, 1=low bitrate, 2=aggressive, 3=very aggressive
            self.vad = webrtcvad.Vad(2)  # Modo agresivo
        else:
            self.vad = None
        
        # Echo Canceller
        if SPEEXDSP_AVAILABLE:
            # SpeexDSP Echo Canceller
            # filter_length: longitud del filtro en samples (ej: 100ms = 1600 samples a 16kHz)
            filter_length = int(sample_rate * 0.1)  # 100ms de eco máximo
            self.echo_canceller = SpeexEchoCanceller(
                frame_size=chunk_size,
                filter_length=filter_length,
                sampling_rate=sample_rate
            )
            self.use_speex = True
        else:
            # Usar cancelador simple
            self.echo_canceller = SimpleEchoCanceller(sample_rate, chunk_size)
            self.use_speex = False
        
        # Estado para VAD
        self.consecutive_voice_frames = 0
        self.consecutive_silence_frames = 0
        self.is_user_speaking = False
        
        # Umbrales
        self.VOICE_FRAMES_THRESHOLD = 3  # ~30ms de voz para considerar que habla
        self.SILENCE_FRAMES_THRESHOLD = 10  # ~100ms de silencio para considerar que terminó
    
    def add_output_audio(self, output_audio: bytes) -> None:
        """
        Añade audio de salida (lo que reproduce el asistente) como referencia
        
        Args:
            output_audio: Audio de salida en bytes (int16)
        """
        if self.use_speex:
            # SpeexDSP maneja esto internamente, no necesitamos hacer nada aquí
            # pero necesitamos pasar el audio de salida cuando procesamos la entrada
            pass
        else:
            # Usar cancelador simple
            self.echo_canceller.add_output_audio(output_audio)
    
    def process_input(self, input_audio: bytes) -> Tuple[bytes, bool]:
        """
        Procesa audio de entrada del micrófono
        
        Args:
            input_audio: Audio de entrada en bytes (int16)
            
        Returns:
            Tuple de (audio_procesado, tiene_voz_usuario)
        """
        # Convertir bytes a numpy array
        input_array = np.frombuffer(input_audio, dtype=np.int16)
        
        # Aplicar echo cancellation
        if self.use_speex:
            # SpeexDSP requiere que pasemos también el audio de salida
            # Por ahora, solo procesamos la entrada
            # TODO: Implementar correctamente con buffer de salida
            processed_array = input_array
        else:
            # Usar cancelador simple
            processed_bytes = self.echo_canceller.process_input(input_audio)
            processed_array = np.frombuffer(processed_bytes, dtype=np.int16)
        
        # Detectar voz del usuario usando WebRTC VAD o detección básica
        has_voice = False
        
        if WEBRTCVAD_AVAILABLE and self.vad is not None:
            # Usar WebRTC VAD
            # VAD necesita frames de 10ms, 20ms o 30ms
            # A 16kHz: 10ms = 160 samples, 20ms = 320, 30ms = 480
            frame_duration_ms = 30  # 30ms frames para VAD
            frame_size = int(self.sample_rate * frame_duration_ms / 1000)  # 480 samples
            
            # Dividir el chunk en frames de 30ms y verificar VAD
            for i in range(0, len(processed_array), frame_size):
                frame = processed_array[i:i+frame_size]
                if len(frame) < frame_size:
                    # Rellenar el último frame si es necesario
                    frame = np.pad(frame, (0, frame_size - len(frame)), mode='constant')
                
                # Convertir a bytes para VAD (necesita bytes)
                frame_bytes = frame.tobytes()
                
                try:
                    # VAD retorna True si detecta voz
                    if self.vad.is_speech(frame_bytes, self.sample_rate):
                        has_voice = True
                        break
                except Exception:
                    # Si VAD falla, usar detección básica por energía
                    energy = np.abs(frame).mean()
                    if energy > 500:
                        has_voice = True
                        break
        else:
            # Detección básica por energía si VAD no está disponible
            # Umbral muy bajo para ser más permisivo
            energy = np.abs(processed_array).mean()
            has_voice = energy > 200  # Umbral muy bajo
        
        # Actualizar estado de habla del usuario
        if has_voice:
            self.consecutive_voice_frames += 1
            self.consecutive_silence_frames = 0
            if self.consecutive_voice_frames >= self.VOICE_FRAMES_THRESHOLD:
                self.is_user_speaking = True
        else:
            self.consecutive_voice_frames = 0
            self.consecutive_silence_frames += 1
            if self.consecutive_silence_frames >= self.SILENCE_FRAMES_THRESHOLD:
                self.is_user_speaking = False
        
        # Convertir de vuelta a bytes
        processed_bytes = processed_array.tobytes()
        
        return processed_bytes, self.is_user_speaking


class AudioProcessor:
    """
    Procesador de audio que combina echo cancellation y VAD
    """
    
    def __init__(self, sample_rate: int = 16000, buffer_size: int = 1024):
        """
        Inicializa el procesador de audio
        
        Args:
            sample_rate: Frecuencia de muestreo
            buffer_size: Tamaño del buffer
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.echo_canceller = RobustEchoCanceller(sample_rate, buffer_size)
        self.enabled = True
    
    def process_output(self, output_audio: bytes) -> None:
        """
        Procesa el audio de salida (lo que reproduce el asistente)
        
        Args:
            output_audio: Audio de salida en bytes
        """
        if not self.enabled:
            return
        
        self.echo_canceller.add_output_audio(output_audio)
    
    def process_input(self, input_audio: bytes, current_time: float) -> Tuple[bytes, bool]:
        """
        Procesa el audio de entrada (del micrófono)
        
        Args:
            input_audio: Audio de entrada en bytes
            current_time: Tiempo actual (no usado, pero mantenido para compatibilidad)
            
        Returns:
            Tuple de (audio procesado, hay_voz_usuario)
        """
        if not self.enabled:
            return input_audio, False
        
        return self.echo_canceller.process_input(input_audio)
    
    def enable(self):
        """Habilita el procesamiento"""
        self.enabled = True
    
    def disable(self):
        """Deshabilita el procesamiento"""
        self.enabled = False
