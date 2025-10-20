[app]

# (str) Title of your application
title = VOERE Scan

# (str) Package name
package.name = voerescan

# (str) Package domain (needed for android/ios packaging)
package.domain = org.voere

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,md,txt

# (str) Application versioning (method 1)
version = 1.0

# (str) Application description
description = VOERE Dokumentenscan App für Fertigungsaufträge und Waffenbuch

# (str) Application author
author = VOERE

# (str) Application email
email = info@voere.at

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.2.0,kivymd==1.1.1,pillow,opencv-python,numpy,python-dateutil

# (str) Main application entry point  
# Buildozer sucht automatisch nach main.py

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, sensorLandscape, portrait, sensorPortrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = False

# (list) Permissions
android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET, ACCESS_NETWORK_STATE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1