from jnius import autoclass, cast
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.app import MDApp
from threading import Thread
import time
import socketio

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

        # Inizializza l'oggetto PythonActivity
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        self.android_activity = PythonActivity.mActivity

        # Avvia il riconoscimento vocale in un thread separato
        thread = Thread(target=self.listen_for_speech)
        thread.daemon = True
        thread.start()

        return kv

    def listen_for_speech(self):
        # Creazione dell'oggetto SpeechRecognizer
        SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')

        # Creazione dell'oggetto Intent per il riconoscimento vocale
        recognizer_intent = autoclass('android.content.Intent')()
        recognizer_intent.setAction("android.speech.action.RECOGNIZE_SPEECH")
        recognizer_intent.putExtra("android.speech.extra.LANGUAGE_MODEL", "free_form")

        # Avvio del riconoscimento vocale
        recognizer = SpeechRecognizer.createSpeechRecognizer(self.android_activity)
        recognizer.setRecognitionListener(SpeechRecognitionListener())
        recognizer.startListening(recognizer_intent)

    def on_stop(self):
        # Ferma l'ascolto quando l'app viene chiusa
        self.android_activity.onActivityResult = None

    @staticmethod
    @sio.on('response')
    def receive_response(response):
        print("Risposta dal server:", response)

class SpeechRecognitionListener(autoclass('android.speech.RecognitionListener')):
    def onResults(self, bundle):
        # Ottenere i risultati del riconoscimento vocale
        results = bundle.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)

        if results:
            transcription = results.get(0)
            print(transcription)

            # Dividi la trascrizione in parole
            words = transcription.split()

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

                    # Verifica se è passato più di 3 secondi tra una parola e l'altra
                    current_time = time.time()
                    if current_time - AuraApp.last_word_time > 3:
                        break

                    AuraApp.last_word_time = current_time

    def onError(self, error):
        print("Errore nel riconoscimento vocale:", error)

    def onReadyForSpeech(self, params):
        print("Pronto per il riconoscimento vocale")

    def onBeginningOfSpeech(self):
        print("Inizio del riconoscimento vocale")

    def onEndOfSpeech(self):
        print("Fine del riconoscimento vocale")

    def onPartialResults(self, partialResults):
        print("Risultati parziali del riconoscimento vocale:", partialResults)

    def onEvent(self, eventType, params):
        print("Evento del riconoscimento vocale:", eventType)

if __name__ == "__main__":
    sio.connect('http://10.10.10.200:8000')  # Connessione al server Flask
    AuraApp().run()
