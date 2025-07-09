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

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, available_timezones
from dataclasses import dataclass
from typing import List, Tuple
import sys
import shutil
from whenami.utils.config import load_config, get_work_hours, get_personal_hours, get_default_timezone

# Color constants
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'


def get_terminal_width():
    """Get terminal width, fallback to 80 if unable to determine"""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80


def create_separator(text=None, width=None, slots=None):
    """Create a separator line that matches the content width"""
    if width is not None:
        return '─' * width

    # If slots provided, calculate width based on longest slot
    if slots:
        max_len = 0
        for slot in slots:
            slot_text = f"• {slot}"
            max_len = max(max_len, len(slot_text))
        return '─' * max_len

    # Fallback to text length or terminal width
    if text:
        import re
        clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
        return '─' * len(clean_text)

    return '─' * get_terminal_width()


@dataclass
class TimeSlot:
    start: datetime
    end: datetime
    is_busy: bool = False
    event_name: str = None

    def __str__(self):
        return f"{format_datetime(self.start)} to {format_datetime(self.end)}"

    def duration(self) -> timedelta:
        return self.end - self.start


def list_timezones():
    """List all available timezones"""
    for tz in sorted(available_timezones()):
        print(tz)
    sys.exit(0)


def convert_timezone(dt, target_tz):
    """Convert datetime to target timezone"""
    return dt.astimezone(ZoneInfo(target_tz))


def get_calendar_info(service, calendar_id):
    """Get calendar timezone and other info"""
    try:
        calendar = service.calendars().get(calendarId=calendar_id).execute()
        return calendar.get('timeZone', 'UTC')
    except Exception:
        return 'UTC'


def get_timezone(tz_name):
    from zoneinfo import ZoneInfo
    try:
        return ZoneInfo(tz_name)
    except Exception as e:
        print(f"[WARNING] Could not load timezone {tz_name}: {e}")
        return ZoneInfo('UTC')


def get_date_range(args, tz):
    today = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)

    if args.today or not any([args.tomorrow, args.next_week, args.next_two_weeks, args.date, getattr(args, 'date_range', None)]):
        return today, today + timedelta(days=1)
    elif args.tomorrow:
        tomorrow = today + timedelta(days=1)
        return tomorrow, tomorrow + timedelta(days=1)
    elif args.next_week:
        # Calculate days until next Monday
        days_until_monday = (7 - today.weekday())
        next_monday = today + timedelta(days=days_until_monday)
        return next_monday, next_monday + timedelta(weeks=1)
    elif args.next_two_weeks:
        return today, today + timedelta(weeks=2)
    elif getattr(args, 'date_range', None):
        # Parse date range in format "start,end"
        try:
            start_str, end_str = args.date_range.split(',')
            start_str = start_str.strip().replace('/', '-')
            end_str = end_str.strip().replace('/', '-')

            # Try 4-digit year first, then 2-digit year
            try:
                start_date = datetime.strptime(start_str, "%d-%m-%Y")
            except ValueError:
                start_date = datetime.strptime(start_str, "%d-%m-%y")

            try:
                end_date = datetime.strptime(end_str, "%d-%m-%Y")
            except ValueError:
                end_date = datetime.strptime(end_str, "%d-%m-%y")

            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=tz)

            return (start_date, end_date)
        except ValueError:
            print(f"[ERROR] Invalid date range format '{args.date_range}'. Please use 'DD/MM/YYYY,DD/MM/YYYY' or 'DD/MM/YY,DD/MM/YY'.")
            sys.exit(1)
    elif args.date is not None:
        # If args.date is a non-empty string, parse it directly
        if args.date and isinstance(args.date, str):
            try:
                # Support both DD/MM/YYYY, DD-MM-YYYY, DD/MM/YY, and DD-MM-YY formats
                date_str = args.date.replace('/', '-')

                # Try 4-digit year first
                try:
                    single_date = datetime.strptime(date_str, "%d-%m-%Y")
                except ValueError:
                    # Try 2-digit year
                    single_date = datetime.strptime(date_str, "%d-%m-%y")

                start_date = single_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
                end_date = single_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=tz)
                return (start_date, end_date)
            except ValueError:
                print(f"[ERROR] Invalid date format '{args.date}'. Please use DD/MM/YYYY, DD-MM-YYYY, DD/MM/YY, or DD-MM-YY.")
                sys.exit(1)
        else:
            # Interactive mode (when --date is passed without value)
            try:
                start_date = datetime.strptime(input("Enter start date (DD-MM-YYYY): "), "%d-%m-%Y")
                end_date = datetime.strptime(input("Enter end date (DD-MM-YYYY): "), "%d-%m-%Y")

                # Set start to beginning of day and end to beginning of next day
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
                end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=tz)

                # If same date, make it a full day
                if start_date.date() == end_date.date():
                    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                return (start_date, end_date)
            except ValueError:
                print("[ERROR] Invalid date format. Please use DD-MM-YYYY.")
                sys.exit(1)


def is_workday(date):
    # Monday = 0, Friday = 4
    return date.weekday() < 5


def is_in_mid_day_break(dt, break_start_time, break_end_time):
    """Check if datetime is within mid-day break"""
    if not (break_start_time and break_end_time):
        return False

    dt_time = dt.time()
    return break_start_time <= dt_time < break_end_time


def filter_time_hours(slots: List[TimeSlot], config: dict, args) -> List[TimeSlot]:
    """Filter slots based on personal/work hours and handle mid-day breaks"""
    # If --all-hours is specified, skip all time filtering
    if getattr(args, 'all_hours', False):
        return slots

    # Determine which hours to use
    if args.work_hours:
        # Use work hours when explicitly requested
        time_start, time_end, break_start, break_end = get_work_hours(config)
    else:
        # Use personal hours as default (unless --all-hours)
        time_start, time_end, break_start, break_end = get_personal_hours(config)
    time_start_time = datetime.strptime(time_start, '%H:%M').time()
    time_end_time = datetime.strptime(time_end, '%H:%M').time()
    break_start_time = datetime.strptime(break_start, '%H:%M').time() if break_start else None
    break_end_time = datetime.strptime(break_end, '%H:%M').time() if break_end else None

    filtered_slots = []
    for slot in slots:
        current = slot.start
        while current < slot.end:
            if not args.work_days or is_workday(current):
                # Set time bounds for the current day
                day_start = current.replace(
                    hour=time_start_time.hour,
                    minute=time_start_time.minute,
                    second=0
                )
                day_end = current.replace(
                    hour=time_end_time.hour,
                    minute=time_end_time.minute,
                    second=0
                )

                # Adjust slot boundaries
                slot_start = max(current, day_start)
                slot_end = min(slot.end, day_end)

                # Split slot if it crosses mid-day break
                if slot_start < slot_end and break_start_time and break_end_time:
                    break_start_dt = current.replace(
                        hour=break_start_time.hour,
                        minute=break_start_time.minute,
                        second=0
                    )
                    break_end_dt = current.replace(
                        hour=break_end_time.hour,
                        minute=break_end_time.minute,
                        second=0
                    )

                    # Add slot before break if exists
                    if slot_start < break_start_dt:
                        pre_break_end = min(slot_end, break_start_dt)
                        filtered_slots.append(TimeSlot(slot_start, pre_break_end, is_busy=slot.is_busy, event_name=slot.event_name))

                    # Add slot after break if exists
                    if slot_end > break_end_dt:
                        post_break_start = max(slot_start, break_end_dt)
                        filtered_slots.append(TimeSlot(post_break_start, slot_end, is_busy=slot.is_busy, event_name=slot.event_name))
                else:
                    if slot_start < slot_end:
                        filtered_slots.append(TimeSlot(slot_start, slot_end, is_busy=slot.is_busy, event_name=slot.event_name))

            # Move to next day
            next_day = current.replace(hour=0, minute=0, second=0) + timedelta(days=1)
            current = next_day

    return filtered_slots


def get_calendar_timezone(service, calendar_id):
    try:
        calendar = service.calendars().get(calendarId=calendar_id).execute()
        return calendar.get('timeZone', 'UTC')
    except Exception:
        return 'UTC'


def organize_slots(busy_times: List[Tuple[str, str, str]], start_date: datetime, end_date: datetime,
                   tz: ZoneInfo) -> List[TimeSlot]:
    """Organize both busy and free slots chronologically"""
    all_slots = []
    current_time = start_date

    for start, end, event_name in busy_times:
        start_dt = parse_datetime(start, tz)
        end_dt = parse_datetime(end, tz)

        # Add free slot before busy period if exists
        if current_time < start_dt:
            all_slots.append(TimeSlot(current_time, start_dt, is_busy=False))

        # Add busy slot
        all_slots.append(TimeSlot(start_dt, end_dt, is_busy=True, event_name=event_name))
        current_time = end_dt

    # Add remaining free slot if exists
    if current_time < end_date:
        all_slots.append(TimeSlot(current_time, end_date, is_busy=False))

    return all_slots


def filter_short_slots(slots: List[TimeSlot], min_duration_minutes: int) -> List[TimeSlot]:
    """Filter out slots that are shorter than minimum duration"""
    if not min_duration_minutes:
        return slots

    min_duration = timedelta(minutes=min_duration_minutes)
    return [slot for slot in slots if slot.duration() >= min_duration]


def get_adjusted_duration(slot: TimeSlot, break_start_time: datetime.time, break_end_time: datetime.time) -> timedelta:
    """Calculate slot duration excluding mid-day breaks"""
    if not (break_start_time and break_end_time):
        return slot.duration()

    duration = timedelta()
    current_date = slot.start.date()
    current = slot.start

    while current.date() <= slot.end.date():
        # Get end time for current day
        day_end = min(
            slot.end,
            datetime.combine(current.date(), datetime.max.time()).replace(tzinfo=current.tzinfo)
        )

        if current < day_end:
            # Calculate break period for this day
            break_start = datetime.combine(current_date, break_start_time).replace(tzinfo=current.tzinfo)
            break_end = datetime.combine(current_date, break_end_time).replace(tzinfo=current.tzinfo)

            if current < break_end and day_end > break_start:
                # Add duration before break if any
                if current < break_start:
                    duration += min(break_start, day_end) - current
                # Add duration after break if any
                if day_end > break_end:
                    duration += day_end - max(break_end, current)
            else:
                # No break overlap, add full duration
                duration += day_end - current

        # Move to next day
        next_day = current.date() + timedelta(days=1)
        current = datetime.combine(next_day, datetime.min.time()).replace(tzinfo=current.tzinfo)
        current_date = current.date()

    return duration


def display_slots(slots: List[TimeSlot], target_tz: str = None, split: bool = False, min_duration_minutes: int = 0,
                  args=None):
    """Display slots based on filter options"""
    if not slots:
        print("No slots to display")
        return

    # Convert target_tz string to ZoneInfo object if provided
    if target_tz:
        if hasattr(args, 'debug') and args.debug:
            print(f"[DEBUG] Converting slots to timezone: {target_tz}")
        target_timezone = get_timezone(target_tz)

    # Convert all slots to target timezone if specified
        slots = [
            TimeSlot(
                start=slot.start.astimezone(target_timezone),
                end=slot.end.astimezone(target_timezone),
                is_busy=slot.is_busy,
                event_name=slot.event_name
            )
            for slot in slots
        ]

    free_slots = []
    busy_slots = []
    total_free = timedelta()
    total_busy = timedelta()

    config = load_config()
    _, _, break_start, break_end = get_work_hours(config)
    break_start_time = datetime.strptime(break_start, '%H:%M').time() if break_start else None
    break_end_time = datetime.strptime(break_end, '%H:%M').time() if break_end else None

    for slot in slots:
        duration = get_adjusted_duration(slot, break_start_time, break_end_time)

        if slot.is_busy:
            total_busy += duration
            if args.show_busy:
                busy_slots.append(slot)
        else:
            if duration >= timedelta(minutes=min_duration_minutes):
                total_free += duration
                if args.show_free:
                    free_slots.append(slot)
    title = f"WHENAMI {Colors.GREEN}free{Colors.RESET}/{Colors.RED}busy{Colors.RESET}?"
    print(f"\n{title}")

    if split:
        if args.show_busy and busy_slots:
            title = f"{Colors.RED}Busy{Colors.RESET} slots"
            print(f"\n{title}")
            print(f"{create_separator(slots=busy_slots)}")
            for slot in busy_slots:
                if getattr(args, 'event_name', False) and slot.event_name:
                    print(f"{Colors.RED}• {slot} - {slot.event_name}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}• {slot}{Colors.RESET}")
            print(f"{create_separator(slots=busy_slots)}")
            print(f"Total {Colors.RED}busy{Colors.RESET} time: {Colors.RED}{Colors.BOLD}{format_duration(total_busy)}{Colors.RESET}")

        if args.show_free and free_slots:
            title = f"{Colors.GREEN}Free{Colors.RESET} slots"
            print(f"\n{title}")
            print(f"{create_separator(slots=free_slots)}")
            for slot in free_slots:
                print(f"{Colors.GREEN}• {slot}{Colors.RESET}")
            print(f"{create_separator(slots=free_slots)}")
            print(f"Total {Colors.GREEN}free{Colors.RESET} time: {Colors.GREEN}{Colors.BOLD}{format_duration(total_free)}{Colors.RESET}")
    else:
        all_display_slots = sorted(busy_slots + free_slots, key=lambda x: x.start)
        print(f"{create_separator(slots=all_display_slots)}")
        for slot in all_display_slots:
            if slot.is_busy:
                if getattr(args, 'event_name', False) and slot.event_name:
                    print(f"{Colors.RED}• {slot} - {slot.event_name}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}• {slot}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}• {slot}{Colors.RESET}")
        print(f"{create_separator(slots=all_display_slots)}")
        if args.show_free:
            print(f"Total {Colors.GREEN}free{Colors.RESET} time: {Colors.GREEN}{Colors.BOLD}{format_duration(total_free)}{Colors.RESET}")
        if args.show_busy:
            print(f"Total {Colors.RED}busy{Colors.RESET} time: {Colors.RED}{Colors.BOLD}{format_duration(total_busy)}{Colors.RESET}")


def format_duration(td: timedelta) -> str:
    """Format timedelta in a readable way"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours == 0:
        return f"{minutes} minutes"
    elif minutes == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minutes"


def merge_busy_periods(busy_periods_list: List[List[dict]]) -> List[dict]:
    """Merge busy periods from multiple calendars"""
    all_periods = []
    for periods in busy_periods_list:
        all_periods.extend(periods)

    # Sort by start time
    all_periods.sort(key=lambda x: x['start'])

    # Merge overlapping periods
    merged = []
    for period in all_periods:
        if not merged or merged[-1]['end'] < period['start']:
            merged.append(period)
        else:
            # When merging overlapping periods, combine event names
            merged[-1]['end'] = max(merged[-1]['end'], period['end'])
            if merged[-1].get('summary') and period.get('summary'):
                merged[-1]['summary'] = f"{merged[-1]['summary']} / {period['summary']}"
            elif period.get('summary'):
                merged[-1]['summary'] = period['summary']

    return merged


def get_calendars_info(service, calendar_ids: List[str]) -> dict:
    """Get calendar info for multiple calendars"""
    calendars_info = {}
    for cal_id in calendar_ids:
        try:
            calendar = service.calendars().get(calendarId=cal_id).execute()
            calendars_info[cal_id] = {
                'timezone': calendar.get('timeZone', 'UTC'),
                'name': calendar.get('summary', cal_id)
            }
        except Exception as e:
            print(f"[WARNING] Could not get info for calendar {cal_id}: {e}")
    return calendars_info


def find_free_slots(service, start_date, end_date, calendar_ids,
                    config=None, target_tz=None, split=False, args=None):
    """Find free slots in calendars"""
    if hasattr(args, 'debug') and args.debug:
        print("\n[DEBUG] Searching for slots in multiple calendars...")
    try:
        # Get calendars info
        calendars_info = get_calendars_info(service, calendar_ids)
        if not calendars_info:
            print("[ERROR] No valid calendars found!")
            return

        # Use configured default timezone or system timezone
        config_tz = get_default_timezone(config)
        tz = config_tz
        if hasattr(args, 'debug') and args.debug:
            print(f"[DEBUG] Using timezone: {tz}")

        # Get busy periods from all calendars
        busy_periods_list = []
        for cal_id in calendar_ids:
            if getattr(args, 'event_name', False):
                # Use events API to get event names
                try:
                    events_result = service.events().list(
                        calendarId=cal_id,
                        timeMin=start_date.isoformat(),
                        timeMax=end_date.isoformat(),
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()

                    events = events_result.get('items', [])
                    cal_busy = []
                    for event in events:
                        # Skip all-day events or events without start/end times
                        if 'dateTime' in event.get('start', {}) and 'dateTime' in event.get('end', {}):
                            cal_busy.append({
                                'start': event['start']['dateTime'],
                                'end': event['end']['dateTime'],
                                'summary': event.get('summary', 'Untitled Event')
                            })

                    if cal_busy:
                        if hasattr(args, 'debug') and args.debug:
                            print(f"me[DEBUG] Found {len(cal_busy)} busy periods in {calendars_info[cal_id]['name']}")
                        busy_periods_list.append(cal_busy)
                except Exception as e:
                    print(f"[WARNING] Failed to fetch events for calendar {cal_id}: {e}")
            else:
                # Use freebusy API for performance when event names aren't needed
                body = {
                    "timeMin": start_date.isoformat(),
                    "timeMax": end_date.isoformat(),
                    "items": [{"id": cal_id}],
                    "timeZone": start_date.tzname()
                }

                try:
                    result = service.freebusy().query(body=body).execute()
                    cal_busy = result.get('calendars', {}).get(cal_id, {}).get('busy', [])
                    if cal_busy:
                        if hasattr(args, 'debug') and args.debug:
                            print(f"\n[DEBUG] Found {len(cal_busy)} busy periods in {calendars_info[cal_id]['name']}")
                        # Add None for event name to match expected format
                        cal_busy = [{'start': period['start'], 'end': period['end'], 'summary': None} for period in cal_busy]
                        busy_periods_list.append(cal_busy)
                except Exception as e:
                    print(f"[WARNING] Failed to fetch calendar {cal_id}: {e}")

        if not any(busy_periods_list):
            print("No events found. All calendars are free!")
            return

        # Merge busy periods from all calendars
        merged_busy_periods = merge_busy_periods(busy_periods_list)

        # Organize and display slots
        all_slots = organize_slots(
            [(p['start'], p['end'], p.get('summary')) for p in merged_busy_periods],
            start_date, end_date, tz
        )

        # Apply time filtering (personal hours by default, unless --all-hours specified)
        all_slots = filter_time_hours(all_slots, config, args)

        # Get minimum slot duration from config
        min_duration = config.get('minimum_slot_duration', 30)
        if hasattr(args, 'debug') and args.debug:
            print(f"[DEBUG] Minimum free slot duration: {min_duration} minutes")

        display_slots(all_slots, target_tz, split, min_duration, args)

    except Exception as e:
        print(f"[ERROR] Failed to fetch calendar events: {str(e)}")
        sys.exit(1)


def parse_datetime(dt_str, tz):
    """Parse datetime string from freebusy API response"""
    try:
        # Try parsing with offset
        if '+' in dt_str or '-' in dt_str:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        else:
            # Parse UTC format and set UTC timezone
            dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        # Convert to target timezone
        return dt.astimezone(tz)
    except ValueError as e:
        print(f"[DEBUG] Failed to parse datetime: {dt_str}")
        raise e


def format_datetime(dt, target_tz=None):
    """Format datetime in a more readable way"""
    if isinstance(dt, str):
        try:
            if '+' in dt or '-' in dt:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"[DEBUG] Failed to parse datetime string: {dt}")
            raise

    # No need to convert here since slots are already converted in display_slots
    return f"{dt.strftime('%Y-%m-%d %H:%M')} {dt.tzname()}"
