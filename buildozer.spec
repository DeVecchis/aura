[app]

# (str) Nome dell'app
title = NomeApp

# (str) Package dell'app
package.name = nomeapp

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
android.ndk_path = /home/riccardo/android-ndk-r21d
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
#buildozer.version = 1.2.0

# (list) Configurazione aggiuntiva per Android
android.permissions = INTERNET, RECORD_AUDIO
android.api = 29
android.sdk = 29
android.ndk = 21.4.7075529
android.gradle_dependencies = com.android.support:support-annotations:28.0.0, com.android.support:support-v4:28.0.0, com.android.support:appcompat-v7:28.0.0, com.android.support:design:28.0.0, com.google.firebase:firebase-analytics:17.2.2, com.google.firebase:firebase-messaging:20.2.4, com.google.firebase:firebase-crashlytics:17.0.1, com.google.firebase:firebase-perf:19.0.3, com.crashlytics.sdk.android:crashlytics:2.10.1
android.gradle_add_repo = 'maven { url "https://jitpack.io" }'
