from kivy.lang import Builder
from kivy.animation import Animation
from kivy.clock import Clock
from kivymd.app import MDApp
from threading import Thread
import speech_recognition as sr
import time
import socketio
import pyttsx3

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

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.last_word_time = time.time()

        # Avvia il riconoscimento vocale in un thread separato
        thread = Thread(target=self.listen_for_speech)
        thread.daemon = True
        thread.start()

        return kv

    def listen_for_speech(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        while True:
            with self.microphone as source:
                audio = self.recognizer.listen(source)

            try:
                # Ottieni la trascrizione dal riconoscimento vocale
                transcription = self.recognizer.recognize_google(audio, language="it-IT")
                print(transcription)
                # Dividi la trascrizione in parole
                words = transcription.split()

                # Verifica se la parola "Aura" è stata pronunciata
                if "Aura" in words:
                    # Ottieni l'indice della parola "Aura"
                    aura_index = words.index("Aura")

                    # Estrai le parole successive alla parola "Aura"
                    aura_words = words[aura_index + 1:]

                    # Stampa le parole dopo la parola "Aura" fino a quando non passano più di 3 secondi tra una parola e l'altra
                    for word in aura_words:
                        print(" ".join(aura_words))
                        sentence = " ".join(aura_words)
                        print(sentence)

                        # Invia la variabile al server
                        sio.emit('sentence', sentence)

                        # Verifica se è passato più di 3 secondi tra una parola e l'altra
                        current_time = time.time()
                        if current_time - self.last_word_time > 3:
                            break

                        self.last_word_time = current_time

            except sr.UnknownValueError:
                print("Non ho capito.")
            except sr.RequestError as e:
                print("Errore nella richiesta di riconoscimento vocale; {0}".format(e))

    def on_stop(self):
        # Ferma l'ascolto quando l'app viene chiusa
        self.microphone.__exit__(None, None, None)


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
    sio.connect('http://127.0.0.1:5000')  # Connessione al server Flask
    AuraApp().run()
