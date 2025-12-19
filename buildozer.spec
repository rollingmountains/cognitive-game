[app]

# Basic info
title = Cognitive Fun
package.name = cognitivequote
package.domain = org.rollingmountains
source.dir = .
source.include_exts = py,json

# [app] section
android.release_artifact = apk

# Version
version = 0.1

# Requirements
requirements = python3==3.11.9,kivy,requests

# Orientation
orientation = portrait

# Android architectures
android.archs = arm64-v8a, armeabi-v7a

# Python for Android branch
p4a.branch = stable

# Skip SQLite and other unwanted stuff
p4a.blacklist_requirements = sqlite3

[buildozer]

# Logging
log_level = 2
warn_on_root = 1
