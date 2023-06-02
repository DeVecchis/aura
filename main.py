from jnius import autoclass, cast, PythonJavaClass, java_method
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.app import MDApp
from threading import Thread
import time
import socketio

sio = socketio.Client()

class SpeechRecognitionListener(PythonJavaClass):
    __javainterfaces__ = ['android/speech/RecognitionListener']

    def __init__(self, callback):
        super(SpeechRecognitionListener, self).__init__()
        self.callback = callback

    @java_method('(I)V')
    def onResults(self, requestCode, resultCode, data):
        results = data.getStringArrayListExtra('android.speech.extra.RESULTS')
        if results:
            transcription = results.get(0)
            self.callback(transcription)


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
        speech_recognizer = autoclass('android.speech.SpeechRecognizer').createSpeechRecognizer(
            self.android_activity)
        recognition_listener = SpeechRecognitionListener(self.on_speech_result)
        speech_recognizer.setRecognitionListener(recognition_listener)

        intent = autoclass('android.content.Intent').setAction('android.speech.action.RECOGNIZE_SPEECH')
        self.android_activity.startActivityForResult(intent, 0)

    def on_stop(self):
        # Ferma l'ascolto quando l'app viene chiusa
        self.android_activity.onActivityResult = None

    def on_speech_result(self, transcription):
        print(transcription)

        words = transcription.split()

        aura_index = ''
        if "Maura" in words:
            aura_index = words.index("Maura")
        elif "Aura" in words:
            aura_index = words.index("Aura")
        elif "Laura" in words:
            aura_index = words.index("Laura")

        if aura_index:
            aura_words = words[aura_index + 1:]

            for word in aura_words:
                print(" ".join(aura_words))
                sentence = " ".join(aura_words)
                print(sentence)

                sio.emit('sentence', sentence)

                current_time = time.time()
                if current_time - self.last_word_time > 3:
                    break

                self.last_word_time = current_time

    @staticmethod
    @sio.on('response')
    def receive_response(response):
        print("Risposta dal server:", response)

if __name__ == "__main__":
    sio.connect('http://10.10.10.200:8000')  # Connessione al server Flask
    AuraApp().run()
