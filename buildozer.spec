[app]
title = My Daily Routine Manager
package.name = routinemanager
package.domain = org.routineapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.build_tools = 33.0.2
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
