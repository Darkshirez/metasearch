[app]
title = MetaSearch
package.name = metasearch
package.domain = com.metasearch
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt,ttf
version = 3.0.0
requirements = python3,kivy==2.2.1,pillow,requests,urllib3,certifi,charset_normalizer,idna,beautifulsoup4,lxml,soupsieve
orientation = portrait
fullscreen = 0

# Android
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = armeabi-v7a
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = @android:style/Theme.NoTitleBar
android.presplash_color = #0a0e17
android.window_background = #0a0e17
android.logcat_filters = *:S python:D

# Buildozer
buildozer.warn_on_root = 1
