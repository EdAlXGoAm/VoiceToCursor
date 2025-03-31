from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class AudioController:
    def __init__(self):
        # Inicializar el controlador de volumen usando pycaw
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.original_volume = None

    def get_volume(self):
        # Obtener el volumen actual del sistema como porcentaje (0-100)
        return self.volume.GetMasterVolumeLevelScalar() * 100

    def set_volume(self, vol_percent):
        # Establecer el volumen del sistema a un porcentaje dado (0-100)
        if vol_percent < 0 or vol_percent > 100:
            raise ValueError("El volumen debe estar entre 0 y 100")
        self.volume.SetMasterVolumeLevelScalar(vol_percent / 100, None)

    def mute(self):
        # Silenciar el sonido del sistema
        self.volume.SetMute(1, None)

    def unmute(self):
        # Reactivar el sonido del sistema
        self.volume.SetMute(0, None)

    def silence(self):
        # Guardar el volumen actual y silenciar el sistema
        self.original_volume = self.get_volume()
        self.mute()

    def restore(self):
        # Restaurar el volumen original y reactivar el sonido
        if self.original_volume is not None:
            self.unmute()
            self.set_volume(self.original_volume)
            self.original_volume = None

    def set_default_volume(self, default_volume=50.0):
        # Establecer el volumen del sistema a un nivel predeterminado
        self.set_volume(default_volume) 