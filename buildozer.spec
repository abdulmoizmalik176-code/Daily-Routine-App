[app]
title = My Daily Routine Manager
package.name = routinemanager
package.domain = org.routineapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.encoding = utf-8
android.archs = arm64-v8a
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# ======= ICON SETTING =======
icon.filename = %(source.dir)s/icon.png
# ============================

[buildozer]
log_level = 2
warn_on_root = 0

[android]
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.gles_version = 3
