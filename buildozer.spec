[app]

# (str) Nome dell'app
title = Aura

# (str) Package dell'app
package.name = aura

# (str) Versione dell'app
package.version = 0.1
version = 0.1.0
# (str) Descrizione dell'app
description = Descrizione dell'app

# (str) Icona dell'app (deve essere un file PNG e rispettare le dimensioni richieste)

# (str) Directory principale dell'app
source.dir = .

# (list) Elenco di tutti i file da includere nell'app
source.include_exts = py,png,jpg,kv,atlas
android.ndk_path = /home/riccardo/android-ndk-r25c
# (list) Elenco di tutti i moduli da includere nell'app
source.include_patterns = assets/*,images/*.png,fonts/*

# (list) Elenco di tutti i moduli da escludere dall'app
source.exclude_patterns = tests/*,venv/*,.git/*,buildozer.spec,*.md,*.pyc,*__pycache__/*

# (str) Nome del file principale da eseguire
source.main_python_file = aura.py

# (list) Elenco di dipendenze esterne
requirements = python3, kivy, kivymd, pyaudio, SpeechRecognition, pyttsx3, socketio


# (str) Imposta l'orientamento predefinito dell'app (portrait, landscape, all)
orientation = portrait

# (bool) Abilita il debug
log_level = 2

# (str) URL dell'API di buildozer (non modificare)
#buildozer.url = https://github.com/kivy/buildozer/archive/master.zip

# (str) Versione di buildozer da utilizzare (opzionale, se specificato buildozer.url verrà ignorato)
#buildozer.version = 1.5.1

# (list) Configurazione aggiuntiva per Android
android.permissions = INTERNET, RECORD_AUDIO
android.api = 30
android.ndk = 25.0.7075529
