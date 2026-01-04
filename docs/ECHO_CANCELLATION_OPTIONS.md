# Opciones para Cancelación de Eco Acústico (AEC)

## Problema
El asistente captura su propia voz del altavoz, causando feedback loop y autorespuestas. Necesitamos eliminar la voz del asistente del audio del micrófono.

## Opciones Disponibles

### 1. **WebRTC Audio Processing (Recomendado)**
**Biblioteca**: `webrtcvad` + procesamiento personalizado
- ✅ Diseñado para tiempo real
- ✅ Bajo latency
- ⚠️ Requiere implementación de AEC manual
- **Instalación**: `pip install webrtcvad`

### 2. **SpeechBrain**
**Biblioteca**: `speechbrain`
- ✅ Framework completo con módulos de enhancement
- ✅ Incluye AEC y noise reduction
- ✅ Basado en PyTorch
- ⚠️ Puede tener más latency
- **Instalación**: `pip install speechbrain`

### 3. **NoiseReduce**
**Biblioteca**: `noisereduce`
- ✅ Fácil de usar
- ✅ Reducción de ruido general
- ⚠️ No específico para echo cancellation
- **Instalación**: `pip install noisereduce`

### 4. **Librosa + Procesamiento de Señal**
**Biblioteca**: `librosa` + `scipy`
- ✅ Muy flexible
- ✅ Buenas herramientas de análisis
- ⚠️ Requiere implementación completa de AEC
- **Instalación**: `pip install librosa scipy`

### 5. **PyAudio + Procesamiento Manual**
**Biblioteca**: `pyaudio` + `numpy` + `scipy`
- ✅ Control total
- ✅ Bajo overhead
- ⚠️ Requiere implementación completa
- **Ya instalado**

## Recomendación: Implementación Híbrida

1. **Corto plazo**: Usar `webrtcvad` para Voice Activity Detection (VAD) + filtrado básico
2. **Medio plazo**: Implementar AEC simple usando correlación cruzada entre audio de salida y entrada
3. **Largo plazo**: Integrar SpeechBrain para AEC avanzado si es necesario

## Implementación Propuesta

### Fase 1: VAD + Filtrado Básico
- Detectar cuando el asistente está hablando
- Reducir ganancia del micrófono durante ese tiempo
- Usar `webrtcvad` para detectar voz del usuario

### Fase 2: AEC Simple
- Capturar audio de salida (lo que reproduce el asistente)
- Correlacionar con entrada del micrófono
- Restar señal correlacionada de la entrada

### Fase 3: AEC Avanzado (si es necesario)
- Integrar SpeechBrain para AEC basado en ML
- Entrenar modelo específico si es necesario

