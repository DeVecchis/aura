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
        intent = autoclass('android.content.Intent')()
        intent.setAction("android.speech.action.RECOGNIZE_SPEECH")
        intent.putExtra("android.speech.extra.LANGUAGE_MODEL", "free_form")

        # Avvia l'activity di riconoscimento vocale
        self.android_activity.startActivityForResult(intent, 0)

        # Aspetta il risultato dell'attività di riconoscimento vocale
        result = self.android_activity.onActivityResult(0, -1, intent, 0, None)
        print("la variabile result è:",result)
        # Recupera il testo dalla lista dei risultati
        if result and len(result) > 0:
            results_list = result.getStringArrayListExtra(autoclass('android.speech.RecognizerIntent').EXTRA_RESULTS)
            print("la variabile results_list è:",results_list)
            if results_list:
                recognized_text = results_list.get(0)
                print("Testo riconosciuto:", recognized_text)

if __name__ == '__main__':
    AuraApp().run()
