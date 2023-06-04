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

        # Configura il riconoscimento vocale con speech_recognition
        recognizer = sr.Recognizer()

        # Esegui il riconoscimento vocale in un ciclo continuo
        while True:
            # Acquisisci i dati audio
            audio_record.read(audio_buffer, 0, buffer_size)

            # Converte i dati audio in formato utilizzabile da SpeechRecognition
            audio_data = bytes(audio_buffer)

            # Crea un oggetto AudioData utilizzando i dati audio
            audio = sr.AudioData(audio_data, sample_rate, sample_width=2)

            # Converte l'audio in testo utilizzando speech_recognition
            try:
                text = recognizer.recognize_google(audio.get_raw_data(), language="it-IT")
                print("Testo riconosciuto:", text)
            except sr.UnknownValueError:
                print("Impossibile convertire l'audio in testo.")
            except sr.RequestError as e:
                print("Errore durante la richiesta al servizio di riconoscimento vocale:", str(e))

            # Dividi la trascrizione in parole
            words = text.split()

            aura_index = ''
            # Verifica se la parola "Aura" è stata pronunciata
            if "Maura" in words:
                aura_index = words.index("Maura")
            elif "Aura" in words:
                aura_index = words.index("Aura")
            elif "Laura" in words:
                aura_index = words.index("Laura")

            if aura_index:
                # Estrai le parole successive alla parola "Aura"
                aura_words = words[aura_index + 1:]

                # Stampa le parole dopo la parola "Aura" fino a quando non passano più di 3 secondi tra una parola e l'altra
                for word in aura_words:
                    print(" ".join(aura_words))
                    sentence = " ".join(aura_words)
                    print(sentence)

                    # Invia la variabile al server
                    sio.emit('sentence', sentence)

                    # # Verifica se è passato più di 3 secondi tra una parola e l'altra
                    # current_time = time.time()
                    # if current_time - self.last_word_time > 3:
                    #     break

                    # self.last_word_time = current_time


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
