import os
import openai
import re
from typing import Optional, Dict, Any, BinaryIO, Union, List

class GPTAudioProcessor:
    """
    Librería especializada para procesar archivos de audio con GPT.
    Permite transcribir audio y procesarlo con modelos de lenguaje.
    """
    
    # Constantes para modelos de transcripción disponibles
    WHISPER_MODEL = "whisper-1"
    GPT4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el procesador de audio con GPT.
        
        Args:
            api_key: API key de OpenAI. Si no se proporciona, se intentará cargar de las variables de entorno.
        """
        # Usar la API key proporcionada o intentar cargarla de las variables de entorno
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("No se proporcionó API key y no se encontró en las variables de entorno")
        
        # Inicializar cliente de OpenAI
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def transcribe_audio(self, 
                         audio_file: Union[str, BinaryIO], 
                         model: str = WHISPER_MODEL, 
                         language: Optional[str] = None,
                         prompt: Optional[str] = None,
                         response_format: str = "text",
                         temperature: Optional[float] = None) -> str:
        """
        Transcribe un archivo de audio utilizando el modelo especificado.
        
        Args:
            audio_file: Ruta al archivo de audio o archivo abierto en modo binario.
            model: Modelo de OpenAI a utilizar para la transcripción.
                  Valores disponibles: "whisper-1", "gpt-4o-mini-transcribe"
            language: Código de idioma opcional para mejorar la transcripción.
            prompt: Texto opcional para guiar la transcripción y mejorar la precisión.
            response_format: Formato de respuesta (default: "text").
            temperature: Controla la aleatoriedad de la transcripción (0-1), solo disponible en algunos modelos.
            
        Returns:
            Texto transcrito del audio.
        """
        # Si audio_file es una ruta de archivo, abrirlo
        file_obj = None
        try:
            if isinstance(audio_file, str):
                file_obj = open(audio_file, "rb")
                file_to_use = file_obj
            else:
                file_to_use = audio_file
                
            # Preparar los parámetros para la transcripción
            params = {
                "model": model,
                "file": file_to_use,
                "response_format": response_format
            }
            
            # Añadir parámetros opcionales si se proporcionan
            if language:
                params["language"] = language
            if prompt:
                params["prompt"] = prompt
            if temperature is not None:
                params["temperature"] = temperature
                
            # Realizar la transcripción
            transcript = self.client.audio.transcriptions.create(**params)
            
            # Manejar diferentes tipos de respuesta
            if response_format == "text":
                # En formato text, el objeto transcript puede ser directamente un string o tener un atributo text
                if hasattr(transcript, 'text'):
                    return transcript.text
                elif isinstance(transcript, str):
                    return transcript
                else:
                    # Intentar convertir a string como último recurso
                    return str(transcript)
            elif response_format == "json":
                # En formato json, puede venir como un objeto con atributo text o un diccionario
                if hasattr(transcript, 'text'):
                    return transcript.text
                elif isinstance(transcript, dict) and 'text' in transcript:
                    return transcript['text']
                else:
                    # Intentar convertir a string como último recurso
                    return str(transcript)
            else:
                # Para otros formatos, intentar obtener el texto de la mejor manera posible
                if hasattr(transcript, 'text'):
                    return transcript.text
                elif isinstance(transcript, str):
                    return transcript
                elif isinstance(transcript, dict) and 'text' in transcript:
                    return transcript['text']
                else:
                    return str(transcript)
            
        finally:
            # Cerrar el archivo si lo abrimos aquí
            if file_obj:
                file_obj.close()
    
    def process_text_with_gpt(self, 
                             text: str, 
                             model: str = "gpt-3.5-turbo", 
                             system_message: str = "Eres un asistente útil.",
                             tag_output: bool = True,
                             tag_name: str = "text_to_cursor",
                             temperature: float = 0.7,
                             max_tokens: Optional[int] = None,
                             additional_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Procesa texto con un modelo de lenguaje GPT.
        
        Args:
            text: Texto a procesar.
            model: Modelo de OpenAI a utilizar (default: "gpt-3.5-turbo").
                  También soporta modelos más nuevos como "gpt-4", "gpt-4o", etc.
            system_message: Mensaje del sistema para definir el comportamiento del asistente.
            tag_output: Si se debe instruir al modelo para que envuelva la respuesta en etiquetas.
            tag_name: Nombre de la etiqueta a utilizar si tag_output es True.
            temperature: Controla la aleatoriedad de las respuestas (0-2).
            max_tokens: Número máximo de tokens en la respuesta.
            additional_params: Parámetros adicionales para la API de OpenAI.
            
        Returns:
            Texto procesado por el modelo.
        """
        # Modificar el mensaje del sistema si se solicita etiquetar la salida
        if tag_output:
            tag_instruction = f" Envuelve tu respuesta exactamente entre etiquetas [{tag_name}] y [/{tag_name}]. No añadas ningún texto adicional fuera de estas etiquetas."
            system_message = system_message + tag_instruction
        
        # Preparar los parámetros para la llamada a la API
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ],
            "temperature": temperature
        }
        
        # Añadir max_tokens si se proporciona
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        # Añadir parámetros adicionales si se proporcionan
        if additional_params:
            params.update(additional_params)
            
        # Realizar la llamada a la API
        response = self.client.chat.completions.create(**params)
        
        # Devolver el contenido de la respuesta
        return response.choices[0].message.content
    
    def _extract_tagged_content(self, text: str, tag_name: str) -> str:
        """
        Extrae el contenido entre etiquetas específicas.
        
        Args:
            text: Texto del que extraer el contenido.
            tag_name: Nombre de la etiqueta.
            
        Returns:
            Contenido extraído entre las etiquetas, o el texto original si no se encuentran las etiquetas.
        """
        pattern = rf"\[{tag_name}\](.*?)\[/{tag_name}\]"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # Si no encontramos las etiquetas, devolvemos el texto original pero limpio
        return text.strip()
    
    def process_audio(self, 
                     audio_file: Union[str, BinaryIO],
                     transcription_model: str = WHISPER_MODEL,
                     process_model: str = "gpt-3.5-turbo", 
                     system_message: str = "Eres un asistente útil.",
                     prompt_template: str = "{text}",
                     tag_name: str = "text_to_cursor",
                     clean_response: bool = True,
                     transcription_prompt: Optional[str] = None,
                     transcription_language: Optional[str] = None) -> str:
        """
        Procesa un archivo de audio: lo transcribe y luego procesa el texto con GPT.
        
        Args:
            audio_file: Ruta al archivo de audio o archivo abierto en modo binario.
            transcription_model: Modelo para transcripción. 
                                Valores disponibles: "whisper-1", "gpt-4o-mini-transcribe"
            process_model: Modelo para procesamiento de texto.
                           Valores disponibles: "gpt-3.5-turbo", "gpt-4", "gpt-4o", etc.
            system_message: Mensaje del sistema para definir el comportamiento del asistente.
            prompt_template: Plantilla para formatear el texto transcrito. Use {text} donde debe ir el texto.
            tag_name: Nombre de la etiqueta para envolver la respuesta.
            clean_response: Si se debe extraer el texto entre etiquetas.
            transcription_prompt: Texto opcional para guiar la transcripción y mejorar la precisión.
            transcription_language: Código de idioma opcional para la transcripción.
            
        Returns:
            Texto procesado por el modelo tras la transcripción.
        """
        # Transcribir el audio con parámetros avanzados
        transcribed_text = self.transcribe_audio(
            audio_file, 
            model=transcription_model,
            language=transcription_language,
            prompt=transcription_prompt
        )
        
        # Formatear el prompt según la plantilla
        formatted_prompt = prompt_template.format(text=transcribed_text)
        
        # Procesar el texto transcrito con instrucción para etiquetar
        processed_text = self.process_text_with_gpt(
            formatted_prompt, 
            model=process_model,
            system_message=system_message,
            tag_output=True,
            tag_name=tag_name
        )
        
        # Extraer el texto entre etiquetas si se solicita
        if clean_response:
            processed_text = self._extract_tagged_content(processed_text, tag_name)
        
        return processed_text
        
    @classmethod
    def get_available_transcription_models(cls) -> List[str]:
        """
        Devuelve la lista de modelos de transcripción disponibles.
        
        Returns:
            Lista de modelos de transcripción soportados.
        """
        return [cls.WHISPER_MODEL, cls.GPT4O_MINI_TRANSCRIBE] 