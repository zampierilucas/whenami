# Whenami

A powerful Google Calendar tool that merges multiple calendars to find your true availability across work and personal schedules.

<img alt="Whenami demo" src="https://raw.githubusercontent.com/zampierilucas/whenami/master/demo.gif" />

## Description

whenami is a command-line tool designed for people who juggle multiple calendars (work, personal, side projects, etc.). Its key strength is **merging multiple Google Calendars** to show your real availability by combining busy periods from all sources.

### Key Features:
- **🗓️ Multi-calendar support**: Connect work calendars, personal Gmail calendars, shared calendars
- **🔀 Smart merging**: Automatically merges busy periods from all calendars to show true availability
- **⏰ Flexible time filtering**: Personal hours (awake time), work hours, or 24/7 view
- **🎨 Color-coded output**: Green for free slots, red for busy periods
- **🌍 Advanced timezone handling**: Automatically detects each calendar's timezone, merges events correctly across timezones, and converts output to any timezone
- **📅 Multiple date ranges**: Today, tomorrow, next week, or custom date ranges

Perfect for professionals who need to see availability across multiple calendars without manually checking each one.

## Installation

### From PyPI (Recommended)
```bash
pip install whenami
```

After installation, you can run the tool directly:
```bash
whenami --help
```

### Local Development Setup

For local development or running from source:

#### Prerequisites
- Python 3.7+

#### Setup
```bash
# Clone the repository
git clone https://github.com/zampierilucas/whenami.git
cd whenami

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run the tool directly (after installation)
whenami --help

# Or run from source
python src/whenami/main.py --help
```

## Usage

Run the tool with various options:

```bash
# Show only free slots for today (default)
whenami

# Show only free slots (same as default)
whenami --free --today

# Show only busy slots
whenami --busy --today

# Split busy and free slots into separate sections
whenami --today --split

# Show free slots for tomorrow
whenami --tomorrow

# Show free slots for next week work days(default mon-fri)
whenami --next-week --work-days

# Show free slots during work hours only
whenami --today --work-hours

# Show free slots during personal hours (default: 8-22)
whenami --today --personal-hours

# Show all hours (24/7, no time filtering)
whenami --today --all-hours

# Convert output to a specific timezone
whenami --today --convert-tz America/Sao_Paulo

# Show event names alongside busy slots
whenami --today --event-name

# Show event names with split view
whenami --today --event-name --split

# List available timezones
whenami --list-tz
```

## Timezone Support

whenami intelligently handles complex timezone scenarios:

### **Multi-Timezone Calendar Merging**
- **Auto-detection**: Automatically detects each calendar's native timezone (e.g., work calendar in EST, personal in PST)
- **Smart merging**: Converts all events to a common timezone before merging busy periods
- **Accurate overlap detection**: Ensures proper conflict detection across timezone boundaries

### **Flexible Output Conversion**
```bash
# View in your local timezone (default)
whenami --today

# Convert to a specific timezone for travel/meetings
whenami --today --convert-tz Europe/London
whenami --next-week --convert-tz Asia/Tokyo

# List all available timezones
whenami --list-tz
```

### **Real-World Example**
If you have:
- Work calendar in `America/New_York` (EST/EDT)
- Personal calendar in `America/Los_Angeles` (PST/PDT)
- University calendar in `Europe/London` (GMT/BST)

whenami will automatically handle the conversions and show your true availability across all timezones, optionally converting the final output to any timezone you specify.

## Configuration

1. Copy the example config file:
```bash
cp config.json.example config.json
```

2. Edit `config.json` with your calendar settings:

```json
{
    "calendars": [
        {
            "id": "your-work-email@company.com",
            "name": "Work Calendar"
        },
        {
            "id": "your-personal@gmail.com",
            "name": "Personal Calendar"
        },
        {
            "id": "shared-project@company.com",
            "name": "Shared Project Calendar"
        },
        {
            "id": "student.name@university.edu",
            "name": "University Calendar"
        }
    ],
    "work_hours": {
        "start": "09:00",
        "end": "17:00"
    },
    "personal_hours": {
        "start": "08:00",
        "end": "22:00"
    },
    "minimum_slot_duration": 30,
    "default_timezone": "Europe/Dublin"
}
```

### Configuration Options

- **`calendars`**: Array of calendar objects with `id` and `name` fields
- **`work_hours`**: Define work hours (start/end times in 24-hour format)
- **`personal_hours`**: Define personal hours (start/end times in 24-hour format)
- **`minimum_slot_duration`**: Minimum duration in minutes for free slots to be displayed
- **`default_timezone`**: Default timezone for date calculations (e.g., "Europe/Dublin", "America/New_York", "UTC")

**📝 Note**: Add as many calendars as needed - the tool will merge all busy periods to show your true availability across all calendars. This is especially useful if you have separate work, personal, and project calendars that you need to coordinate.

The `default_timezone` setting controls the timezone used for date calculations (e.g., "today", "tomorrow"). If not specified, the tool will try to use your system's timezone, falling back to UTC.

## Authentication

The tool requires Google Calendar API authentication:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `credentials.json` in the project root

The first time you run the tool, it will open a browser window for authentication.

## Development

This project uses GitHub Actions for CI/CD:

- **CI Pipeline**: Runs tests on Python 3.9-3.12, generates coverage reports, and validates builds
- **PyPI Publishing**: Automated publishing to PyPI on releases using trusted publishing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for development setup and contribution guidelines.
