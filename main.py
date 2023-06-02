from kivy.lang import Builder
from kivymd.app import MDApp
from threading import Thread
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

        self.android_activity = autoclass('org.kivy.android.PythonActivity')
        self.recognizer_intent = autoclass('android.speech.RecognizerIntent')

        self.last_word_time = time.time()

        # Avvia il riconoscimento vocale in un thread separato
        thread = Thread(target=self.listen_for_speech)
        thread.daemon = True
        thread.start()

        return kv

    def listen_for_speech(self):
        intent = self.recognizer_intent(self.recognizer_intent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(self.recognizer_intent.EXTRA_LANGUAGE_MODEL, self.recognizer_intent.LANGUAGE_MODEL_FREE_FORM)

        # Avvia l'activity di riconoscimento vocale
        self.android_activity.mActivity.startActivityForResult(intent, 0)

    def on_speech_result(self, requestCode, resultCode, data):
        if resultCode == self.android_activity.RESULT_OK:
            # Ottenere i risultati del riconoscimento vocale
            results = data.getStringArrayListExtra(self.recognizer_intent.EXTRA_RESULTS)

            # Processare i risultati (nel tuo caso, convertirli in testo)
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
                        if current_time - self.last_word_time > 3:
                            break

                        self.last_word_time = current_time

    def on_stop(self):
        # Ferma l'ascolto quando l'app viene chiusa
        self.android_activity.mActivity.onActivityResult = None

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
    sio.connect('http://127.0.0.1:8000')  # Connessione al server Flask
    app = AuraApp()
    app.android_activity.mActivity.onActivityResult = app.on_speech_result
    app.run()
