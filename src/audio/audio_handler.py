"""Manejo de audio para entrada y salida"""

import asyncio
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

# Exportar constantes para uso en otros módulos
__all__ = ['FORMAT', 'CHANNELS', 'SEND_SAMPLE_RATE', 'RECEIVE_SAMPLE_RATE', 'CHUNK_SIZE', 'AudioHandler']


class AudioHandler:
    """Maneja la entrada y salida de audio"""

    def __init__(self, pya_instance: pyaudio.PyAudio):
        self.pya = pya_instance
        self.audio_stream = None

    async def open_input_stream(self):
        """Abre el stream de entrada de audio"""
        mic_info = self.pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        return self.audio_stream

    async def read_audio_chunk(self):
        """Lee un chunk de audio del micrófono"""
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        data = await asyncio.to_thread(
            self.audio_stream.read, CHUNK_SIZE, **kwargs
        )
        return {"data": data, "mime_type": "audio/pcm"}

    async def open_output_stream(self):
        """Abre el stream de salida de audio"""
        return await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )

    def close_input_stream(self):
        """Cierra el stream de entrada"""
        if self.audio_stream:
            self.audio_stream.close()

