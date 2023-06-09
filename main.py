from kivy.lang import Builder
from kivymd.app import MDApp
from threading import Thread
import time
import socketio
from jnius import autoclass


sio = socketio.Client()

class AuraApp(MDApp):

    # Inizializza PyJNIus
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    tts = TextToSpeech(mActivity, None)
    # Imposta la lingua di default per la sintesi vocale
    Locale = autoclass('java.util.Locale')
    tts.setLanguage(Locale('it', 'IT'))
    tts.setSpeechRate(1.2)
    PowerManager = autoclass('android.os.PowerManager')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity

    power_manager = activity.getSystemService(activity.POWER_SERVICE)
    wake_lock = power_manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MyWakeLockTag")
    wake_lock.acquire()

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

        # Importa le classi Java necessarie
        AudioRecord = autoclass('android.media.AudioRecord')
        AudioFormat = autoclass('android.media.AudioFormat')
        AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        # Inizializza PyJNIus
        autoclass('org.kivy.android.PythonActivity').mActivity

        # Imposta i parametri audio per l'acquisizione
        sample_rate = 16000  # Frequenza di campionamento in Hz
        channel_config = AudioFormat.CHANNEL_IN_MONO
        audio_format = AudioFormat.ENCODING_PCM_16BIT
        duration_in_seconds = 4
        bytes_per_sample = 2
        num_channels = 1
        buffer_size = sample_rate * bytes_per_sample * num_channels * duration_in_seconds
        print(buffer_size)
        print(audio_format)
        print(channel_config)
        # Inizializza l'oggetto AudioRecord per l'acquisizione audio
        audio_record = AudioRecord(
        AudioSource.MIC,
            sample_rate,
            channel_config,
            audio_format,
            buffer_size
        )

        # Crea un buffer per i dati audio
        audio_buffer = bytearray(buffer_size)

        # Avvia la registrazione audio
        audio_record.startRecording()

        # Esegui il riconoscimento vocale in un ciclo continuo
        while True:
            # Acquisisci i dati audio
            audio_record.read(audio_buffer, 0, buffer_size)

            # Converte i dati audio in formato utilizzabile da SpeechRecognition
            audio_data = bytes(audio_buffer)
            sio.emit('sentence', audio_data)
            time.sleep(2.5)
            # Crea un oggetto AudioData utilizzando i dati audio

    def on_stop(self):
        # Ferma l'ascolto quando l'app viene chiusa
        pass

    @staticmethod
    @sio.on('response')
    def receive_response(response):
        print("Risposta dal server:", response)
        AuraApp.tts.speak(response, AuraApp.TextToSpeech.QUEUE_FLUSH, None)
        print(AuraApp.tts.isSpeaking())
        while AuraApp.tts.isSpeaking():
            
            print("Sta parlando...")
            time.sleep(0.5)

        print("sono dopo tutto")

import socket
import netifaces

def get_local_ip():
        # Ottieni l'indirizzo IP locale
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                for link in addresses[netifaces.AF_INET]:
                    if 'addr' in link:
                        return link['addr']
if __name__ == "__main__":
    local_ip = get_local_ip()
    if "10.10.10" in local_ip:
        sio.connect("http://10.10.10.200:8000")
    else:
        sio.connect("http://176.12.93.138:8000")  # Connessione al server Flask
    AuraApp().run()
