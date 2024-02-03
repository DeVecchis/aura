from kivy.lang import Builder
from kivymd.app import MDApp
from threading import Thread
import time
import socketio
from kivy.animation import Animation
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

        label.center_x = kv.width / 2
        label.center_y = kv.height / 2

        self.last_word_time = time.time()

        # Avvia il riconoscimento vocale in un thread separato
        thread = Thread(target=self.start_recording)
        thread.daemon = True
        thread.start()

        return kv

    def start_recording(self):
        """metto cose"""
        print("sono in start recording:")
        self.button_anim = Animation(size_hint=(0.12, 0.12), duration=0.5) + Animation(size_hint=(0.1, 0.1), duration=0.5)
        self.button_anim.repeat = True
        self.button_anim.start(self.root.ids.record_button)

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
        self.buffer_size = sample_rate * bytes_per_sample * num_channels * duration_in_seconds
        print("buffer_size",self.buffer_size)
        print("audio_format",audio_format)
        print(channel_config)
        # Inizializza l'oggetto AudioRecord per l'acquisizione audio
        self.audio_record = AudioRecord(
        AudioSource.MIC,
            sample_rate,
            channel_config,
            audio_format,
            self.buffer_size
        )
        # Crea un buffer per i dati audio
        self.audio_buffer = bytearray(self.buffer_size)
        # Avvia la registrazione audio
        self.audio_record.startRecording()
        print("ho iniziato la registrazione")

    def stop_recording(self):
        print("sono in stop_recording")
        self.audio_record.stop()
        self.button_anim.stop(self.root.ids.record_button)
        self.root.ids.record_button.size_hint = (0.09, 0.09)
        self.root.ids.spinner.active = True
        self.audio_record.read(self.audio_buffer, 0, self.buffer_size)
        print("######################## AUDIO DATA ###########################")
        # Converte i dati audio in formato utilizzabile da SpeechRecognition
        audio_data = bytes(self.audio_buffer)
        print(audio_data)
        sio.emit('sentence', audio_data)
        pass

    @staticmethod
    @sio.on('response')
    def receive_response(self,response):
        print("sono in response!!!!")
        self.root.ids.spinner.active = False
        self.root.ids.server_output.text = response
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
    print("-----------------------------------------")
    print(local_ip)
    if "192.168.1." in local_ip:
        sio.connect("http://192.168.1.183:8000")
    else:
        sio.connect("http://78.134.67.14:8000")  # Connessione al server Flask
    AuraApp().run()
