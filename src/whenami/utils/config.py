# Copyright 2025 Lucas Zampieri
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

import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo


def get_config_dir():
    """Get the config directory path and create it if it doesn't exist"""
    config_dir = Path.home() / '.config' / 'whenami'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def load_config():
    """Load config from .config/whenami/config.json or fallback to current directory"""
    config_dir = get_config_dir()
    config_path = config_dir / 'config.json'
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to current directory
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[INFO] No config.json found. Please create one at {config_path}")
            return {"default_calendar": None}


def get_default_timezone(config):
    """Get the default timezone from config or system default"""
    # First check config.json
    config_tz = config.get('default_timezone')
    if config_tz:
        try:
            return ZoneInfo(config_tz)
        except Exception:
            print(f"[WARNING] Invalid timezone in config: {config_tz}")
    
    # Fall back to system timezone
    try:
        # Try to get system timezone from TZ environment variable
        tz_name = os.environ.get('TZ')
        if tz_name:
            return ZoneInfo(tz_name)
        
        # Try to read from /etc/timezone (common on Linux)
        try:
            with open('/etc/timezone', 'r') as f:
                tz_name = f.read().strip()
                if tz_name:
                    return ZoneInfo(tz_name)
        except FileNotFoundError:
            pass
            
        # Try to read from /etc/localtime symlink (common on Linux)
        try:
            import os
            link_path = os.readlink('/etc/localtime')
            if '/zoneinfo/' in link_path:
                tz_name = link_path.split('/zoneinfo/')[-1]
                return ZoneInfo(tz_name)
        except (OSError, FileNotFoundError):
            pass
            
    except Exception:
        pass
    
    # Final fallback to UTC
    return ZoneInfo('UTC')


def get_work_hours(config):
    work_hours = config.get('work_hours', {'start': '09:00', 'end': '17:00'})
    mid_day = work_hours.get('mid_day_break', {'start': None, 'end': None})
    return (
        work_hours['start'],
        work_hours['end'],
        mid_day['start'],
        mid_day['end']
    )


def get_personal_hours(config):
    personal_hours = config.get('personal_hours', {'start': '08:00', 'end': '22:00'})
    mid_day = personal_hours.get('mid_day_break', {'start': None, 'end': None})
    return (
        personal_hours['start'],
        personal_hours['end'],
        mid_day['start'],
        mid_day['end']
    )
