# Grabador de Voz para Cursor

Esta aplicación permite grabar tu voz y convertirla en un prompt pulido para Cursor.

## Requisitos

- Python 3.7 o superior
- Micrófono funcional
- Cuenta de OpenAI con API key configurada

## Instalación

1. Clona este repositorio
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura tu API key de OpenAI:
   - Crea un archivo `.env` en la raíz del proyecto
   - Agrega tu API key: `OPENAI_API_KEY=tu_api_key_aquí`

## Uso

1. Ejecuta la aplicación:
```bash
python voice_to_cursor.py
```

2. Configura las opciones avanzadas (opcional):
   - Selecciona el modelo de transcripción: `whisper-1` o `gpt-4o-mini-transcribe`
   - Haz clic en "Explorar Proyecto" para generar automáticamente un prompt de transcripción contextual
   - Especifica el idioma (ej: "es" para español)
   - Elige el modelo GPT para el procesamiento

3. Haz clic en "Iniciar Grabación" para comenzar a grabar
4. Habla lo que necesites
5. Haz clic en "Detener Grabación" cuando termines
6. El texto pulido se copiará automáticamente a tu portapapeles

## Características Destacadas

### Explorador de Proyecto

La aplicación incluye un explorador de proyecto que analiza automáticamente la estructura de archivos y el código fuente para mejorar la precisión de las transcripciones:

- **Análisis de estructura**: Genera un mapa de todos los archivos y carpetas del proyecto
- **Extracción de funciones**: Identifica nombres de funciones en varios lenguajes de programación
- **Prompt contextual**: Crea automáticamente un prompt que orienta al modelo de transcripción
- **Mejora de precisión**: Ayuda al modelo a reconocer correctamente términos técnicos específicos del proyecto

Para utilizar esta característica:
1. Haz clic en el botón "Explorar Proyecto"
2. Espera a que se complete el análisis
3. El prompt generado aparecerá en el campo de texto
4. Puedes editar el prompt manualmente si lo deseas

## Modelos Soportados

### Modelos de Transcripción
- `whisper-1`: Modelo original de Whisper
- `gpt-4o-mini-transcribe`: Nuevo modelo de transcripción basado en GPT-4o, con mayor precisión

### Modelos de Procesamiento
- `gpt-3.5-turbo`: Versión rápida y económica
- `gpt-4`: Mayor capacidad de comprensión
- `gpt-4o`: Última versión con capacidades mejoradas

## Componentes

### GPTAudioProcessor

La aplicación utiliza la librería `GPTAudioProcessor` para procesar archivos de audio con GPT:

```python
from gpt_audio_processor import GPTAudioProcessor

# Inicializar el procesador
processor = GPTAudioProcessor(api_key="tu_api_key")

# Procesar un archivo de audio con etiquetas y opciones avanzadas
resultado = processor.process_audio(
    audio_file="ruta_al_archivo.wav",
    transcription_model="gpt-4o-mini-transcribe",
    process_model="gpt-4o",
    system_message="Instrucciones para el asistente",
    prompt_template="Plantilla para el prompt: {text}",
    tag_name="text_to_cursor",
    clean_response=True,
    transcription_prompt="El audio contiene términos técnicos de programación",
    transcription_language="es"
)
```

### ProjectExplorer

Clase para analizar el proyecto y generar prompts de transcripción contextuales:

```python
from project_explorer import get_project_transcription_prompt

# Generar un prompt de transcripción contextual
prompt = get_project_transcription_prompt("ruta/al/proyecto")
print(prompt)
```

#### Características clave

- **Sistema de etiquetas**: El modelo envuelve el texto resultante entre etiquetas específicas (ej. `[text_to_cursor]` y `[/text_to_cursor]`), facilitando la extracción precisa del contenido relevante.
- **Procesamiento eficiente**: Transcribe audio y lo procesa con modelos GPT en un solo paso.
- **Flexibilidad**: Funciona con rutas de archivo o archivos ya abiertos.
- **Soporte para nuevos modelos**: Compatible con los últimos modelos de OpenAI.
- **Mejora de precisión**: Permite usar prompts específicos para guiar la transcripción.

#### Transcripción con Prompting

Puedes mejorar la precisión de las transcripciones proporcionando un prompt:

```python
# Transcripción con prompt para mejorar el reconocimiento de términos técnicos
texto = processor.transcribe_audio(
    audio_file="audio.mp3",
    model="gpt-4o-mini-transcribe",
    prompt="El audio contiene términos técnicos como API, Python, JavaScript y Docker",
    language="es"
)
```

## Notas

- La aplicación utiliza modelos de OpenAI para la transcripción y procesamiento de texto
- Los archivos de audio temporales se eliminan automáticamente después del procesamiento
- Asegúrate de tener una conexión a internet para usar la API de OpenAI
- Los modelos más avanzados pueden incurrir en mayores costos pero ofrecen mejor calidad 