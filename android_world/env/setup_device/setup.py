# Copyright 2024 The android_world Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup tool for Android World.

It does the following:

* APK Management: Automates installations of apks needed for Android World.
* Sets up environment: Configures emulator with necessary permissions, using adb
  and basic automation.
"""

import os

from absl import logging
from android_env.components import errors
from android_world.env import adb_utils
from android_world.env import interface
from android_world.env.setup_device import apps
from android_world.utils import app_snapshot
import subprocess

# APKs required for Android World.
_APPS = (
    # keep-sorted start
    apps.AndroidWorldApp,
    apps.AudioRecorder,
    apps.CameraApp,
    apps.ChromeApp,
    apps.ClipperApp,
    apps.ClockApp,
    apps.ContactsApp,
    apps.DialerApp,
    apps.ExpenseApp,
    apps.FilesApp,
    apps.JoplinApp,
    apps.MarkorApp,
    apps.MiniWobApp,
    apps.OpenTracksApp,
    apps.OsmAndApp,
    apps.RecipeApp,
    apps.RetroMusicApp,
    apps.SettingsApp,
    apps.SimpleCalendarProApp,
    apps.SimpleDrawProApp,
    apps.SimpleGalleryProApp,
    apps.SimpleSMSMessengerApp,
    apps.TasksApp,
    apps.VlcApp,
    # keep-sorted end
)

_APPS_LABS = (
    "zoom",
    "settings",
    "clock",
    "contacts",
    "bluecoins",
    "cantook",
    "mapme",
    "pimusic",
    "calendar",
)


def _download_and_install_apk(apk: str, env: interface.AsyncEnv) -> None:
  """Downloads all APKs from remote location and installs them."""
  path = apps.download_app_data(apk)
  adb_utils.install_apk(path, env.controller)

import pdb

def _install_all_apks(env: interface.AsyncEnv) -> None:
  """Installs all APKs for Android World."""
  print("Downloading app data and installing apps. This make take a few mins.")
  for app in _APPS:
    if not app.apk_names:  # Ignore 1p apps that don't have an APK.
      continue
    apk_installed = False
    for apk_name in app.apk_names:
      try:
        _download_and_install_apk(apk_name, env)
        apk_installed = True
        # pdb.set_trace()
        break
      except errors.AdbControllerError:
        # Try apk compiled for a different architecture, e.g., Mac M1.
        # pdb.set_trace()
        continue
    if not apk_installed:
      raise RuntimeError(
          f"Failed to download and install APK for {app.app_name}"
      )


def setup_apps(env: interface.AsyncEnv) -> None:
  """Sets up apps for Android World.

  Args:
    env: The Android environment.

  Raises:
    RuntimeError: If cannot install APK.
  """
  # Make sure quick-settings are not displayed, which can override foreground
  # apps, and impede UI navigation required for setting up.
  adb_utils.press_home_button(env.controller)
  adb_utils.set_root_if_needed(env.controller)

  _install_all_apks(env)

  print(
      "Setting up applications on Android device. Please do not interact with"
      " device while installation is running."
  )
  for app in _APPS:
    try:
      logging.info("Setting up app %s", app.app_name)
      app.setup(env)
    except ValueError as e:
      logging.warning(
          "Failed to automatically setup app %s: %s.\n\nYou will need to"
          " manually setup the app.",
          app.app_name,
          e,
      )
    app_snapshot.save_snapshot(app.app_name, env.controller)

def setup_apps_lab(env: interface.AsyncEnv) -> None:
  """Sets up apps for Android World.

  Args:
    env: The Android environment.

  Raises:
    RuntimeError: If cannot install APK.
  """
  # Make sure quick-settings are not displayed, which can override foreground
  # apps, and impede UI navigation required for setting up.
  adb_utils.press_home_button(env.controller)
  adb_utils.set_root_if_needed(env.controller)

  for app in _APPS_LABS:
    app_snapshot.save_snapshot(app, env.controller)


def setup_apps_bench(env: interface.AsyncEnv) -> None:
  """Sets up apps for Android World.

  Args:
    env: The Android environment.

  Raises:
    RuntimeError: If cannot install APK.
  """

  adb_utils.press_home_button(env.controller)
  adb_utils.set_root_if_needed(env.controller)

  apk_files = ['./mobile_agent_benchmark/app/' + f for f in os.listdir('./mobile_agent_benchmark/app') if f.endswith('.apk')]

  for apk in apk_files:
      print(f"Installing {apk} ...")
      try:
          subprocess.run(['adb', '-s', 'emulator-5556', 'install', '-r', apk], check=True)

      except:
          print(f"fail to install {apk} ...")
  