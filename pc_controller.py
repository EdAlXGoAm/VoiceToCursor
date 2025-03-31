import pyautogui
import time

class PcController:
    def __init__(self):
        # Configurar PyAutoGUI para mayor seguridad
        pyautogui.FAILSAFE = True  # Mover el ratón a la esquina superior izquierda detendrá el script
        pyautogui.PAUSE = 0.1  # Pequeño retraso entre acciones

    def click_derecho(self, x, y):
        """Realiza un clic derecho en las coordenadas especificadas"""
        pyautogui.rightClick(x, y)
        
    def click_izquierdo(self, x, y):
        """Realiza un clic izquierdo en las coordenadas especificadas"""
        pyautogui.click(x, y)
        
    def copiar(self):
        """Copia el texto seleccionado actualmente"""
        pyautogui.hotkey('ctrl', 'c')
        # Pequeña pausa para asegurar que la copia se complete
        time.sleep(0.1)
        
    def pegar(self):
        """Pega el texto en la posición actual del cursor"""
        pyautogui.hotkey('ctrl', 'v')
        
    def enter(self):
        """Presiona la tecla Enter"""
        pyautogui.press('enter')
        
    def doble_click(self, x, y):
        """Realiza un doble clic en las coordenadas especificadas"""
        pyautogui.doubleClick(x, y)
        
    def mover_cursor(self, x, y):
        """Mueve el cursor a las coordenadas especificadas sin hacer clic"""
        pyautogui.moveTo(x, y)
        
    def arrastrar(self, x_inicio, y_inicio, x_fin, y_fin, duracion=0.2):
        """Arrastra desde unas coordenadas a otras"""
        pyautogui.moveTo(x_inicio, y_inicio)
        pyautogui.dragTo(x_fin, y_fin, duration=duracion)
        
    def escribir(self, texto):
        """Escribe el texto en la posición actual del cursor"""
        pyautogui.write(texto)
        
    def tecla_presionada(self, tecla):
        """Presiona una tecla específica"""
        pyautogui.press(tecla)
        
    def combinacion_teclas(self, *teclas):
        """Presiona una combinación de teclas simultáneamente"""
        pyautogui.hotkey(*teclas) 