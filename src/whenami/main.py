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

import argparse
from whenami import __version__
from whenami.utils.auth import authenticate_google_calendar
from whenami.utils.calendar import (
    list_timezones, get_calendar_info, get_timezone,
    get_date_range, find_free_slots
)
from whenami.utils.config import load_config, get_default_timezone


def main():
    parser = argparse.ArgumentParser(description='Find free slots in your calendar')
    parser.add_argument('--version', action='version', version=f'whenami {__version__}')
    
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('--today', action='store_true', help='Show free slots for today')
    date_group.add_argument('--tomorrow', action='store_true', help='Show free slots for tomorrow')
    date_group.add_argument('--next-week', action='store_true', help='Show free slots for next week')
    date_group.add_argument('--next-two-weeks', action='store_true', help='Show free slots for next two weeks')
    date_group.add_argument('--date', action='store_true', help='Enter custom date range')

    parser.add_argument('--work-days', action='store_true', help='Show only Monday-Friday slots')
    parser.add_argument('--work-hours', action='store_true', help='Show only work hours (default: 9-5)')
    parser.add_argument('--personal-hours', action='store_true', help='Show only personal hours (default: 8-22)')
    parser.add_argument('--all-hours', action='store_true', help='Show all hours (24/7, disables time filters)')

    parser.add_argument('--convert-tz', help='Convert output to specified timezone (e.g., America/Sao_Paulo)')
    parser.add_argument('--list-tz', action='store_true', help='List all available timezones')

    slot_group = parser.add_mutually_exclusive_group()
    slot_group.add_argument('--free', action='store_true', help='Show only free slots')
    slot_group.add_argument('--busy', action='store_true', help='Show only busy slots')

    parser.add_argument('--split', action='store_true', help='Split busy and free slots into separate sections')
    parser.add_argument('--event-name', action='store_true', help='Show event names alongside busy slots')
    parser.add_argument('--debug', action='store_true', help='Show debug messages')
    args = parser.parse_args()

    # Set display options based on --free and --busy flags
    args.show_free = True if not args.busy else False
    args.show_busy = True if not args.free else False

    if args.list_tz:
        list_timezones()

    service = authenticate_google_calendar()
    config = load_config()

    calendars = config.get('calendars', [])

    if not calendars:
        print("\nNOTE: No calendars configured in config.json")
        calendar_id = input("Enter calendar ID: ")
        calendars = [{"id": calendar_id}]

    calendar_ids = [cal['id'] for cal in calendars]

    # Get date range using configured default timezone or system timezone
    default_tz = get_default_timezone(config)
    start_date, end_date = get_date_range(args, default_tz)

    find_free_slots(service, start_date, end_date, calendar_ids,
                    config=config,
                    target_tz=args.convert_tz,
                    split=args.split,
                    args=args)


if __name__ == '__main__':
    main()
