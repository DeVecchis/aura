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
    

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

        # Crea un'istanza della classe TextToSpeech di Android

        

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
        print("--------------------------------")
        print("SONO IN RESPONSE")
        print("--------------------------------")
        print("Risposta dal server:", response)
        tts = AuraApp.TextToSpeech(AuraApp.mActivity, None)
        # Imposta la lingua di default per la sintesi vocale
        Locale = autoclass('java.util.Locale')
        tts.setLanguage(Locale('it', 'IT'))
        tts.setSpeechRate(1.2)
        tts.speak(response, AuraApp.TextToSpeech.QUEUE_FLUSH, None)
        print(tts.isSpeaking())
        while tts.isSpeaking():
            
            print("Sta parlando...")
            time.sleep(0.5)
        tts.shutdown()

        print("sono dopo tutto")

if __name__ == "__main__":
    sio.connect("http://10.10.10.200:8000")  # Connessione al server Flask
    AuraApp().run()
