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
import sys
from whenami import __version__
from whenami.utils.auth import authenticate_google_calendar
from whenami.utils.calendar import (
    list_timezones, get_calendar_info, get_timezone,
    get_date_range, find_free_slots
)
from whenami.utils.config import load_config, get_default_timezone
from whenami.utils.llm import parse_with_llm, convert_llm_to_args, show_llm_config, test_llm, show_llm_help


def main():
    # Check if first argument is a text query for LLM processing (quoted string)
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        text_query = sys.argv[1]

        # Check if --debug is in the arguments for LLM debug output
        debug_mode = '--debug' in sys.argv[2:]

        llm_result = parse_with_llm(text_query, debug=debug_mode)
        if llm_result:
            # Convert LLM result to command line arguments
            new_args = convert_llm_to_args(llm_result)

            if debug_mode:
                print(f"[LLM DEBUG] Input: '{text_query}'")
                print(f"[LLM DEBUG] LLM Response: {llm_result}")
                print(f"[LLM DEBUG] Generated Command: whenami {' '.join(new_args)}")

            # Replace sys.argv with new arguments
            sys.argv = [sys.argv[0]] + new_args + sys.argv[2:]
        else:
            print(f"[ERROR] Could not parse text query: '{text_query}'")
            sys.exit(1)

    parser = argparse.ArgumentParser(description='Find free slots in your calendar')
    parser.add_argument('--version', action='version', version=f'whenami {__version__}')

    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('--today', action='store_true', help='Show free slots for today')
    date_group.add_argument('--tomorrow', action='store_true', help='Show free slots for tomorrow')
    date_group.add_argument('--next-week', action='store_true', help='Show free slots for next week')
    date_group.add_argument('--next-two-weeks', action='store_true', help='Show free slots for next two weeks')
    date_group.add_argument('--date', type=str, nargs='?', const='', help='Enter custom date (DD/MM/YYYY, DD/MM/YY, DD-MM-YYYY, DD-MM-YY) or prompt')
    date_group.add_argument('--date-range', type=str, help='Enter date range as "start,end" (supports DD/MM/YYYY or DD/MM/YY)')

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

    # LLM configuration and testing
    parser.add_argument('--llm-config', action='store_true', help='Show LLM configuration')
    parser.add_argument('--llm-test', type=str, nargs='?', const='free tomorrow', help='Test LLM with query (default: "free tomorrow")')
    parser.add_argument('--llm-help', action='store_true', help='Show LLM usage instructions')
    args = parser.parse_args()

    # Set display options based on --free and --busy flags
    args.show_free = True if not args.busy else False
    args.show_busy = True if not args.free else False

    if args.list_tz:
        list_timezones()

    # Handle LLM commands
    if args.llm_config:
        show_llm_config()
        return

    if args.llm_test is not None:
        test_llm(args.llm_test)
        return

    if args.llm_help:
        show_llm_help()
        return

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
