"""Módulo para cancelación de eco acústico y procesamiento de audio"""

import numpy as np
from typing import Optional, Tuple
import collections


class SimpleEchoCanceller:
    """
    Cancelador de eco simple usando correlación cruzada.
    Resta el audio de salida del audio de entrada.
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
        self.output_buffer = collections.deque(maxlen=int(sample_rate * 0.5))  # 0.5 segundos
        
        # Factor de atenuación para el eco
        self.attenuation_factor = 0.7
        
    def add_output_audio(self, audio_data: np.ndarray):
        """
        Añade audio de salida al buffer (lo que está reproduciendo el asistente)
        
        Args:
            audio_data: Array de audio de salida
        """
        # Convertir a int16 si es necesario
        if audio_data.dtype != np.int16:
            audio_data = audio_data.astype(np.int16)
        
        # Añadir al buffer
        self.output_buffer.extend(audio_data)
    
    def process_input(self, input_audio: np.ndarray) -> np.ndarray:
        """
        Procesa el audio de entrada eliminando el eco
        
        Args:
            input_audio: Audio del micrófono
            
        Returns:
            Audio procesado sin eco
        """
        if len(self.output_buffer) == 0:
            # No hay audio de salida, devolver entrada sin procesar
            return input_audio
        
        # Convertir a float32 para procesamiento
        input_float = input_audio.astype(np.float32)
        
        # Obtener el audio de salida más reciente (mismo tamaño que entrada)
        output_array = np.array(list(self.output_buffer)[-len(input_audio):], dtype=np.float32)
        
        # Normalizar
        input_float = input_float / 32768.0
        output_array = output_array / 32768.0
        
        # Calcular correlación cruzada para encontrar el delay
        correlation = np.correlate(input_float, output_array, mode='valid')
        
        if len(correlation) > 0:
            # Encontrar el delay máximo
            delay = np.argmax(np.abs(correlation))
            
            # Ajustar el audio de salida según el delay
            if delay < len(output_array):
                aligned_output = output_array[delay:delay+len(input_float)]
                if len(aligned_output) == len(input_float):
                    # Restar el eco (con atenuación)
                    processed = input_float - (aligned_output * self.attenuation_factor)
                else:
                    processed = input_float
            else:
                processed = input_float
        else:
            processed = input_float
        
        # Limitar valores y convertir de vuelta a int16
        processed = np.clip(processed, -1.0, 1.0)
        processed = (processed * 32767.0).astype(np.int16)
        
        return processed


class VoiceActivityDetector:
    """
    Detector de actividad de voz simple usando energía
    """
    
    def __init__(self, sample_rate: int = 16000, energy_threshold: float = 500.0):
        """
        Inicializa el detector de voz
        
        Args:
            sample_rate: Frecuencia de muestreo
            energy_threshold: Umbral de energía para detectar voz
        """
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        self.silence_duration = 0.0
        self.last_voice_time = 0.0
        self.is_speaking = False
    
    def detect(self, audio_data: np.ndarray, current_time: float) -> bool:
        """
        Detecta si hay actividad de voz
        
        Args:
            audio_data: Audio a analizar
            current_time: Tiempo actual
            
        Returns:
            True si hay voz, False si es silencio
        """
        # Calcular energía del audio
        energy = np.abs(audio_data).mean()
        
        if energy > self.energy_threshold:
            self.is_speaking = True
            self.last_voice_time = current_time
            self.silence_duration = 0.0
            return True
        else:
            if self.is_speaking:
                self.silence_duration = current_time - self.last_voice_time
                # Si llevamos más de 0.5s en silencio, consideramos que terminó
                if self.silence_duration > 0.5:
                    self.is_speaking = False
            return False
    
    def is_user_speaking(self) -> bool:
        """Retorna si el usuario está hablando actualmente"""
        return self.is_speaking


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
        self.echo_canceller = SimpleEchoCanceller(sample_rate, buffer_size)
        self.vad = VoiceActivityDetector(sample_rate)
        self.enabled = True
    
    def process_output(self, output_audio: bytes) -> None:
        """
        Procesa el audio de salida (lo que reproduce el asistente)
        
        Args:
            output_audio: Audio de salida en bytes
        """
        if not self.enabled:
            return
        
        # Convertir bytes a numpy array
        audio_array = np.frombuffer(output_audio, dtype=np.int16)
        self.echo_canceller.add_output_audio(audio_array)
    
    def process_input(self, input_audio: bytes, current_time: float) -> Tuple[bytes, bool]:
        """
        Procesa el audio de entrada (del micrófono)
        
        Args:
            input_audio: Audio de entrada en bytes
            current_time: Tiempo actual
            
        Returns:
            Tuple de (audio procesado, hay_voz)
        """
        if not self.enabled:
            return input_audio, False
        
        # Convertir bytes a numpy array
        audio_array = np.frombuffer(input_audio, dtype=np.int16)
        
        # Aplicar echo cancellation
        processed_audio = self.echo_canceller.process_input(audio_array)
        
        # Detectar actividad de voz
        has_voice = self.vad.detect(processed_audio, current_time)
        
        # Convertir de vuelta a bytes
        processed_bytes = processed_audio.tobytes()
        
        return processed_bytes, has_voice
    
    def enable(self):
        """Habilita el procesamiento"""
        self.enabled = True
    
    def disable(self):
        """Deshabilita el procesamiento"""
        self.enabled = False

