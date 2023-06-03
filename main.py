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

        # Inizializza l'oggetto AndroidAudioRecorder
        AndroidAudioRecorder = autoclass('com.smp.soundtouchandroid.AndroidAudioRecorder')

        # Imposta i parametri audio per l'acquisizione
        sample_rate = 16000  # Frequenza di campionamento in Hz
        buffer_size = 1024

        print("Registrazione in corso...")
        while True:
            # Crea un oggetto di registrazione audio Android
            audio_record = AndroidAudioRecorder(sample_rate, buffer_size)

            # Avvia la registrazione audio
            audio_record.start()

            # Acquisisci i dati audio fino a quando desideri
            # Puoi eseguire questa parte in un ciclo o come callback
            audio_buffer = audio_record.read()

            # Ferma la registrazione audio
            audio_record.stop()

            text = ''
            # Converte i dati audio in formato utilizzabile da SpeechRecognition
            audio_data = bytes(audio_buffer)
            audio = sr.AudioData(audio_data, sample_rate, sample_format=16)

            # Converte l'audio in testo utilizzando speech_recognition
            try:
                text = recognizer.recognize_google(audio, language="it-IT")  # Modifica la lingua in base alle tue esigenze
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
