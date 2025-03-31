import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu, Frame, Label, Entry, Checkbutton, BooleanVar, Text, Scrollbar
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
from dotenv import load_dotenv
import pyperclip
from datetime import datetime
import time
from audio_controller import AudioController
import pyautogui
from pc_controller import PcController
from gpt_audio_processor import GPTAudioProcessor
from project_explorer import get_project_transcription_prompt

# Cargar variables de entorno
load_dotenv()

class VoiceRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Grabador de Voz para Cursor")
        self.root.geometry("500x600")  # Aumentar tamaño para nuevas opciones
        
        # Verificar API key
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            messagebox.showerror("Error", "No se encontró la API key de OpenAI. Por favor, configura OPENAI_API_KEY en el archivo .env")
            self.root.destroy()
            return
            
        self.recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.capturando = False
        self.project_path = r"D:\CursorDeployments\Voice to cursor"  # Ruta al proyecto
        
        # Inicializar el procesador de audio GPT
        self.gpt_processor = GPTAudioProcessor(api_key=self.api_key)
        
        # Crear instancia de AudioController
        self.audio_ctrl = AudioController()
        
        # Crear instancia de PcController
        self.pc_ctrl = PcController()
        
        # Configurar el botón de grabación
        self.button = tk.Button(
            self.root,
            text="Iniciar Grabación",
            command=self.toggle_recording,
            width=20,
            height=2
        )
        self.button.pack(pady=10)
        
        # Añadir Label para mostrar coordenadas del cursor
        self.coords_label = tk.Label(
            self.root, 
            text="Posición del cursor: X: 0, Y: 0",
            font=("Arial", 10)
        )
        self.coords_label.pack(pady=5)
        
        # Frame para la captura de coordenadas
        capture_frame = tk.Frame(self.root)
        capture_frame.pack(pady=5)
        
        # Campos para mostrar coordenadas capturadas
        tk.Label(capture_frame, text="X:").grid(row=0, column=0, padx=5)
        self.x_entry = tk.Entry(capture_frame, width=5)
        self.x_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(capture_frame, text="Y:").grid(row=0, column=2, padx=5)
        self.y_entry = tk.Entry(capture_frame, width=5)
        self.y_entry.grid(row=0, column=3, padx=5)
        
        # Botón para capturar coordenadas
        self.capture_button = tk.Button(
            self.root,
            text="Capturar Coordenadas",
            command=self.toggle_capture,
            width=20
        )
        self.capture_button.pack(pady=5)
        
        # Botón para ejecutar secuencia
        self.execute_button = tk.Button(
            self.root,
            text="Ejecutar Secuencia",
            command=self.execute_sequence,
            width=20
        )
        self.execute_button.pack(pady=5)
        
        # Separador
        separator = tk.Frame(self.root, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=10)
        
        # Frame para opciones avanzadas de transcripción
        options_frame = tk.LabelFrame(self.root, text="Opciones Avanzadas", padx=10, pady=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Modelo de transcripción
        models_frame = tk.Frame(options_frame)
        models_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(models_frame, text="Modelo:").pack(side=tk.LEFT, padx=5)
        
        self.transcription_model = StringVar(self.root)
        available_models = self.gpt_processor.get_available_transcription_models()
        self.transcription_model.set(available_models[0])  # valor por defecto
        
        model_menu = OptionMenu(models_frame, self.transcription_model, *available_models)
        model_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botón para explorar proyecto y generar prompt
        explore_frame = tk.Frame(options_frame)
        explore_frame.pack(fill=tk.X, pady=5)
        
        self.explore_button = tk.Button(
            explore_frame,
            text="Explorar Proyecto",
            command=self.explore_project,
            width=20
        )
        self.explore_button.pack(side=tk.TOP, pady=5)
        
        # Campo para prompt de transcripción con scroll
        prompt_frame = tk.Frame(options_frame)
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(prompt_frame, text="Prompt de transcripción:").pack(side=tk.TOP, anchor="w", padx=5)
        
        # Crear un widget Text con scrollbar para el prompt
        prompt_container = tk.Frame(prompt_frame)
        prompt_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.transcription_prompt_text = Text(prompt_container, height=6, width=50, wrap=tk.WORD)
        self.transcription_prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = Scrollbar(prompt_container, command=self.transcription_prompt_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transcription_prompt_text.config(yscrollcommand=scrollbar.set)
        
        # Campo para idioma
        lang_frame = tk.Frame(options_frame)
        lang_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(lang_frame, text="Idioma:").pack(side=tk.LEFT, padx=5)
        
        self.language_var = StringVar(self.root)
        self.language_var.set("es")  # Valor por defecto: español
        
        self.language_entry = tk.Entry(lang_frame, width=5, textvariable=self.language_var)
        self.language_entry.pack(side=tk.LEFT, padx=5)
        
        # Modelo de procesamiento
        process_frame = tk.Frame(options_frame)
        process_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(process_frame, text="Modelo GPT:").pack(side=tk.LEFT, padx=5)
        
        self.process_model = StringVar(self.root)
        self.process_model.set("gpt-3.5-turbo")  # valor por defecto
        
        process_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
        process_menu = OptionMenu(process_frame, self.process_model, *process_models)
        process_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Iniciar actualización de coordenadas
        self.update_cursor_position()
    
    def explore_project(self):
        """
        Explora el proyecto para generar un prompt de transcripción automático.
        """
        try:
            # Mostrar indicador de carga
            self.explore_button.config(text="Analizando...", state=tk.DISABLED)
            self.root.update()
            
            # Obtener el prompt de transcripción basado en el proyecto
            prompt = get_project_transcription_prompt(self.project_path)
            
            # Limpiar el campo de texto actual
            self.transcription_prompt_text.delete(1.0, tk.END)
            
            # Insertar el nuevo prompt
            self.transcription_prompt_text.insert(tk.END, prompt)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Proyecto analizado correctamente. El prompt de transcripción se ha actualizado.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar el proyecto: {str(e)}")
        finally:
            # Restaurar el botón
            self.explore_button.config(text="Explorar Proyecto", state=tk.NORMAL)
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.recording = True
        self.button.config(text="Detener Grabación")
        self.audio_data = []
        self.audio_ctrl.silence()
        
        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_data.extend(indata[:, 0])
        
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=callback
        )
        self.stream.start()
    
    def stop_recording(self):
        self.recording = False
        self.button.config(text="Iniciar Grabación")
        self.stream.stop()
        self.stream.close()
        self.audio_ctrl.restore()
        
        # Guardar el archivo de audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        wav.write(filename, self.sample_rate, np.array(self.audio_data))
        
        # Procesar el audio
        self.process_audio(filename)
    
    def process_audio(self, audio_file):
        try:
            # Obtener valores de los campos de opciones
            transcription_model = self.transcription_model.get()
            process_model = self.process_model.get()
            
            # Obtener el prompt de transcripción (si hay)
            transcription_prompt = self.transcription_prompt_text.get(1.0, tk.END).strip()
            if not transcription_prompt:
                transcription_prompt = None
            
            # Obtener el idioma (si hay)
            language = self.language_var.get() if self.language_var.get() else None
            
            # Utilizar la librería GPTAudioProcessor con el nuevo enfoque de etiquetas y opciones avanzadas
            polished_text = self.gpt_processor.process_audio(
                audio_file=audio_file,
                transcription_model=transcription_model,
                process_model=process_model,
                system_message="Eres un asistente que ayuda a pulir y mejorar textos para usarlos como prompts en Cursor.",
                prompt_template="Por favor, pulir y mejorar el siguiente texto para usarlo como prompt en Cursor: {text}",
                tag_name="text_to_cursor",
                clean_response=True,
                transcription_prompt=transcription_prompt,
                transcription_language=language
            )
            
            # Copiar al portapapeles
            pyperclip.copy(polished_text)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "El texto pulido ha sido copiado al portapapeles.")
            
            # Eliminar el archivo de audio
            os.remove(audio_file)
            
            # Verificar si hay coordenadas y ejecutar automáticamente la secuencia
            if self.x_entry.get() and self.y_entry.get():
                self.root.after(1000, self.execute_sequence)  # Esperar 1 segundo antes de ejecutar
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el audio: {str(e)}")
    
    def update_cursor_position(self):
        """Actualiza la posición del cursor en tiempo real"""
        try:
            x, y = pyautogui.position()
            self.coords_label.config(text=f"Posición del cursor: X: {x}, Y: {y}")
        except Exception as e:
            print(f"Error al obtener posición del cursor: {e}")
        
        # Actualizar cada 100ms
        self.root.after(100, self.update_cursor_position)
    
    def toggle_capture(self):
        """Activa/desactiva el modo de captura de coordenadas"""
        if not self.capturando:
            self.capturando = True
            self.capture_button.config(text="Esperando clic...")
            # Crear una ventana transparente en pantalla completa para capturar el clic
            self.overlay = tk.Toplevel(self.root)
            self.overlay.attributes('-alpha', 0.01)  # Casi invisible
            self.overlay.attributes('-topmost', True)
            self.overlay.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            self.overlay.bind("<Button-1>", self.capture_click)
        else:
            self.reset_capture_mode()
    
    def capture_click(self, event):
        """Captura las coordenadas del clic y las muestra en los campos"""
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(event.x_root))
        
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(event.y_root))
        
        self.reset_capture_mode()
    
    def reset_capture_mode(self):
        """Resetea el modo de captura"""
        self.capturando = False
        self.capture_button.config(text="Capturar Coordenadas")
        # Cerrar ventana overlay si existe
        if hasattr(self, 'overlay') and self.overlay.winfo_exists():
            self.overlay.destroy()
    
    def execute_sequence(self):
        """Ejecuta una secuencia de comandos usando PC_Controller"""
        try:
            # Verificar si los campos están vacíos
            if not self.x_entry.get() or not self.y_entry.get():
                messagebox.showinfo("Información", "No hay coordenadas para ejecutar la secuencia")
                return
            
            # Obtener coordenadas de los campos de texto
            try:
                x = int(self.x_entry.get())
                y = int(self.y_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Las coordenadas deben ser números enteros")
                return
            
            # Ejecutar secuencia: Enter -> Clic -> Enter
            self.pc_ctrl.enter()
            
            # Pequeña pausa para dar tiempo a que se procese la acción
            time.sleep(0.5)
            
            # Clic en las coordenadas almacenadas
            self.pc_ctrl.click_izquierdo(x, y)
            
            # Pequeña pausa para dar tiempo a que se procese la acción
            time.sleep(0.5)
            
            # Pegar texto del portapapeles
            self.pc_ctrl.pegar()
            
            # Pequeña pausa para dar tiempo a que se procese la acción
            time.sleep(0.5)
            
            # Presionar Enter nuevamente
            self.pc_ctrl.enter()
            
            messagebox.showinfo("Éxito", "Secuencia ejecutada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar la secuencia: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceRecorder()
    app.run() 