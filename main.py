from kivy.lang import Builder
from kivymd.app import MDApp
from threading import Thread
import androidhelper
import time
import socketio
import pyttsx3
import speech_recognition as sr
from jnius import autoclass
from pydub import AudioSegment
import io

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

        # Configura il riconoscimento vocale con SpeechRecognition
        recognizer = sr.Recognizer()

        # Crea un oggetto Android
        droid = androidhelper.Android()

        # Imposta i parametri audio per l'acquisizione
        sample_rate = 16000  # Frequenza di campionamento in Hz
        sample_width = 2  # Dimensione del campione in byte (16-bit = 2 byte)
        channels = 1  # Numero di canali audio (mono)

        # Calcola la dimensione del buffer audio in base alla frequenza di campionamento
        buffer_size = int(sample_rate * sample_width * channels)

        # Avvia la registrazione audio utilizzando MediaRecorder
        droid.recorderStartMicrophone()

        # Avvia il riconoscimento vocale in tempo reale
        while True:
            # Ottieni i dati audio in tempo reale
            audio_data = droid.recorderRead(buffer_size)[1]  # Legge il buffer di dati audio

            # Crea un oggetto AudioData utilizzando i dati audio
            audio = sr.AudioData(audio_data, sample_rate, sample_width)

            # Utilizza SpeechRecognition per il riconoscimento vocale
            try:
                text = recognizer.recognize_google(audio, language="it-IT")
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
