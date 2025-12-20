[app]

# Basic info
title = Cognitive Fun
package.name = cognitivequote
package.domain = org.rollingmountains
source.dir = .
source.include_exts = py,json,png,jpg,kv,atlas

# Version
version = 0.1

# Requirements
requirements = python3,kivy,requests

# Orientation
orientation = portrait

# Android settings
android.release_artifact = apk
android.accept_sdk_license = True
android.sdk = 24
android.ndk = 25b
android.ndk_api = 21
android.minapi = 21
android.api = 33

# Use only one architecture for testing
android.arch = arm64-v8a

# Permissions
android.permissions = INTERNET

[buildozer]

# Logging
log_level = 2
warn_on_root = 1