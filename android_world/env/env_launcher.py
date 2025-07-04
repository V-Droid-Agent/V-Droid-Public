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

"""Launches the environment used in the benchmark."""

import resource

from absl import logging
from android_world.env import adb_utils
from android_world.env import android_world_controller
from android_world.env import interface
from android_world.env.setup_device import setup
from android_world.utils import datetime_utils

import pdb
# AndroidWorld is tested and developed on Pixel 6 with API 33. Other
# configurations may be supported, but are not yet tested.
_ANDROID_WORLD_API_LEVEL = 33  ## original 33


def _get_env(
    console_port: int, adb_path: str, grpc_port: int
) -> interface.AsyncEnv:
  """Creates an AsyncEnv by connecting to an existing Android environment."""
  controller = android_world_controller.get_controller(
      console_port, adb_path, grpc_port
  )
  return interface.AsyncAndroidEnv(controller)

def  _get_env_with_device(
    device_id: int, console_port: int, adb_path: str, grpc_port: int
) -> interface.AsyncEnv:
  """Creates an AsyncEnv by connecting to an existing Android environment."""
  controller = android_world_controller.get_controller_for_device(
      device_id, console_port, adb_path, grpc_port
  )
  return interface.AsyncAndroidEnv(controller)


def verify_api_level(env: interface.AsyncEnv) -> None:
  """Verifies that the emulator's API level is expected."""
  level = adb_utils.get_api_level(env.controller)
  if level != _ANDROID_WORLD_API_LEVEL:
    raise ValueError(
        f'Emulator API level must be {_ANDROID_WORLD_API_LEVEL}, but found'
        f' {level}.'
    )


def _increase_file_descriptor_limit(limit: int = 32768):
  """Increases the file descriptor limit to the given limit.

  This helps with different platforms having different limits, which can result
  from too many open files, sockets, or pipes, resulting in "OSError: [Errno 24]
  Too many open files".

  Args:
    limit: The new file descriptor limit. The default value was determined
      experimentally to not raise too many open files error.
  """
  try:
    _, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    if limit > hard:
      logging.warning(
          (
              "Requested limit %d exceeds the system's hard limit %d. Setting"
              ' to the maximum allowed value.'
          ),
          limit,
          hard,
      )
      limit = hard
    resource.setrlimit(resource.RLIMIT_NOFILE, (limit, hard))
    logging.info('File descriptor limit set to %d.', limit)
  except ValueError as e:
    logging.exception('Failed to set file descriptor limit: %s', e)


def setup_env(
    env: interface.AsyncEnv,
    emulator_setup: bool = True,
    freeze_datetime: bool = True,
    family: str = 'android_lab',
) -> None:
  """Performs environment setup and validation."""
  _increase_file_descriptor_limit()
  if emulator_setup:
    logging.info('Setting up apps on the emulator.')
    # pdb.set_trace()
    if family ==  'android_world':
      setup.setup_apps(env)
    elif family ==  'android_lab':
      setup.setup_apps_lab(env)
    elif family == 'mobile_agent_bench':
      setup.setup_apps_bench(env)
    
  if freeze_datetime:
    logging.info('Freezing datetime.')
    # if family ==  'android_lab':
    #   datetime_utils.setup_datetime(env.controller, )
    # else:
    if family == 'android_lab':
      datetime_utils.setup_datetime_lab(env.controller)
    else:
      datetime_utils.setup_datetime(env.controller)


def load_and_setup_env(
    console_port: int = 5554,
    emulator_setup: bool = False,
    freeze_datetime: bool = True,
    adb_path: str = android_world_controller.DEFAULT_ADB_PATH,
    grpc_port: int = 8554,
    device_name: str = 'Y5FY5HROKR99E6JN',
    family: str= 'android_world',
) -> interface.AsyncEnv:
  """Create environment with `get_env()` and perform env setup and validation.

  Before running this, an emulator must be launched. For example:

  ```
  AVD_NAME=Pixel_6_API_33  # First create an AVD in Android Studio.
  ~/Android/Sdk/emulator/emulator -avd $AVD_NAME -no-snapshot -grpc 8554
  ```

  Args:
    console_port: The console port of the existing device. This can usually be
      retrieved by looking at the output of `adb devices`. In general, the first
      connected device is port 5554, the second is 5556, and so on.
    emulator_setup: Perform first-time app setup on the environment if True.
    freeze_datetime: Whether to freeze the datetime to a fixed time, October
      2023, to ensure consistent benchmarking.
    adb_path: The location of the adb binary.
    grpc_port: The port for gRPC communication with the emulator.

  Returns:
    An interactable Android environment.
  """
  # env = _get_env(console_port, adb_path, grpc_port)
  env = _get_env_with_device(device_name, console_port, adb_path, grpc_port)
  setup_env(env, emulator_setup, freeze_datetime, family)
  return env
