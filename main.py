from kivy.lang import Builder
from kivy.utils import platform
from kivymd.app import MDApp
from threading import Thread
import time
import socketio
import pyttsx3
import speech_recognition as sr
from jnius import autoclass
from android.permissions import request_permissions, Permission

sio = socketio.Client()

class AuraApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

        kv = Builder.load_file("aura.kv")
        label = kv.ids.label

        label.font_size = 100
        label.center_x = kv.width / 2
        label.center_y = kv.height / 2

        self.last_word_time = time.time()

        # Avvia il riconoscimento vocale in un thread separato
        thread = Thread(target=self.listen_for_speech)
        thread.daemon = True
        thread.start()

        return kv

    def listen_for_speech(self):
        # Configura il riconoscimento vocale con speech_recognition
        recognizer = sr.Recognizer()

        # Richiedi i permessi RECORD_AUDIO
        self.request_permissions()

        # Imposta i parametri audio per l'acquisizione
        sample_rate = 16000  # Frequenza di campionamento in Hz
        channel_config = autoclass('android.media.AudioFormat').CHANNEL_IN_MONO
        audio_format = autoclass('android.media.AudioFormat').ENCODING_PCM_16BIT
        buffer_size = autoclass('android.media.AudioRecord').getMinBufferSize(sample_rate, channel_config, audio_format)

        # Inizializza l'oggetto AudioRecord per l'acquisizione audio
        audio_record = autoclass('android.media.AudioRecord')(
            autoclass('android.media.MediaRecorder$AudioSource').MIC,
            sample_rate,
            channel_config,
            audio_format,
            buffer_size
        )

        print("Registrazione in corso...")
        # Avvia la registrazione audio
        audio_record.startRecording()

    def request_permissions(self):
        permission = Permission.RECORD_AUDIO
        request_permissions([permission])

        # Verifica se i permessi sono stati concessi
        if permission in self.get_granted_permissions():
            pass  # I permessi sono stati concessi
        else:
            pass  # Gestisci il caso in cui i permessi non sono stati concessi

    def get_granted_permissions(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity

        PackageManager = autoclass('android.content.pm.PackageManager')
        package_manager = context.getPackageManager()

        permissions = autoclass('android.Manifest$permission')
        granted_permissions = []

        for permission in Permission:
            if package_manager.checkPermission(permission, context.getPackageName()) == PackageManager.PERMISSION_GRANTED:
                granted_permissions.append(permission)

        return granted_permissions

if __name__ == "__main__":
    sio.connect('http://10.10.10.200:8000')  # Connessione al server Flask
    AuraApp().run()
