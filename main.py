from kivy.lang import Builder
from kivymd.app import MDApp
from threading import Thread
import time
import socketio
from plyer import tts, stt

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
        while True:
            try:
                transcription = stt.recognize()
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

            except stt.UnknownValueError:
                print("Non ho capito.")
            except stt.RequestError as e:
                print("Errore nella richiesta di riconoscimento vocale; {0}".format(e))

    def on_stop(self):
        # Ferma l'ascolto quando l'app viene chiusa
        pass

    @staticmethod
    @sio.on('response')
    def receive_response(response):
        print("Risposta dal server:", response)
        tts.speak(response)

if __name__ == "__main__":
    sio.connect('http://10.10.10.200:8000')  # Connessione al server Flask
    AuraApp().run()
