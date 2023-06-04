from kivy.lang import Builder
from kivymd.app import MDApp
from threading import Thread
import time
import socketio
import pyttsx3
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
        buffer_size = AudioRecord.getMinBufferSize(sample_rate, channel_config, audio_format)
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
            time.sleep(5)
            # Crea un oggetto AudioData utilizzando i dati audio

    def on_stop(self):
        # Ferma l'ascolto quando l'app viene chiusa
        pass

    @staticmethod
    @sio.on('response')
    def receive_response(response):
        print("Risposta dal server:", response)
        # Esegui le operazioni necessarie con la risposta
        # Riproduci la risposta tramite sintesi vocale
        engine = pyttsx3.init()
        
        # Imposta la voce femminile in italiano
        engine.setProperty('voice', 'it')
        
        engine.setProperty('rate', 150)  # Velocità della voce (default: 200)
        engine.say(response)
        engine.runAndWait()
        engine.stop()

if __name__ == "__main__":
    sio.connect('http://10.10.10.200:8000')  # Connessione al server Flask
    AuraApp().run()
