from kivy.lang import Builder
from kivymd.app import MDApp
from threading import Thread
import time
import socketio
import pyttsx3
import speech_recognition as sr
from jnius import autoclass

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

        # Importa le classi Java necessarie
        AudioRecord = autoclass('android.media.AudioRecord')
        AudioFormat = autoclass('android.media.AudioFormat')
        AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        Environment = autoclass('android.os.Environment')
        print("--------------------------------")
        print(AudioSource.__dict__)
        print("--------------------------------")
        # Inizializza PyJNIus
        autoclass('org.kivy.android.PythonActivity').mActivity

        # Imposta i parametri audio per l'acquisizione
        sample_rate = 16000  # Frequenza di campionamento in Hz
        channel_config = AudioFormat.CHANNEL_IN_MONO
        audio_format = AudioFormat.ENCODING_PCM_16BIT
        buffer_size = AudioRecord.getMinBufferSize(sample_rate, channel_config, audio_format)

        # Inizializza l'oggetto AudioRecord per l'acquisizione audio
        audio_record = AudioRecord(
            AudioSource.MIC,
            sample_rate,
            channel_config,
            audio_format,
            buffer_size
        )
        print("Registrazione in corso...")
            # Avvia la registrazione audio
        print(audio_record.__dict__)
        audio_record.startRecording()

if __name__ == "__main__":
    sio.connect('http://10.10.10.200:8000')  # Connessione al server Flask
    AuraApp().run()
