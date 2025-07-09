# Whenami

A powerful Google Calendar tool that merges multiple calendars to find your true availability across work and personal schedules.

<img alt="Whenami demo" src="https://raw.githubusercontent.com/zampierilucas/whenami/master/demo.gif" />

## Description

whenami is a command-line tool designed for people who juggle multiple calendars (work, personal, side projects, etc.). Its key strength is **merging multiple Google Calendars** to show your real availability by combining busy periods from all sources.

### Key Features:
- **🗓️ Multi-calendar support**: Connect work calendars, personal Gmail calendars, shared calendars
- **🔀 Smart merging**: Automatically merges busy periods from all calendars to show true availability
- **🤖 AI-powered natural language (optional)**: Use plain English to query your calendar - "free tomorrow", "busy next week"
- **⏰ Flexible time filtering**: Personal hours (awake time), work hours, or 24/7 view
- **🎨 Color-coded output**: Green for free slots, red for busy periods
- **🌍 Advanced timezone handling**: Automatically detects each calendar's timezone, merges events correctly across timezones, and converts output to any timezone
- **📅 Multiple date ranges**: Today, tomorrow, next week, or custom date ranges with flexible date formats

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

**Optional AI features**: LLM support is disabled by default. To enable natural language queries, see the [AI-Powered Natural Language Queries](#ai-powered-natural-language-queries-optional) section below.

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

## AI-Powered Natural Language Queries (Optional)

whenami supports **optional** natural language processing using LLM models via [litellm](https://github.com/BerriAI/litellm), allowing you to query your calendar using plain English. Works with **any LLM service** including OpenAI, Claude, local Ollama, or custom APIs.

**Note**: LLM features are **disabled by default** and require manual configuration to enable.

### Quick Examples
```bash
# Natural language queries
whenami "free tomorrow"
whenami "busy next week"
whenami "work hours today"
whenami "personal time on 15/07/25"
whenami "show me August 2025"

# With debug output to see LLM processing
whenami "free tomorrow" --debug
```

### Setup LLM Features

#### Option 1: Local Ollama (Recommended)
```bash
# Visit https://ollama.ai for installation instructions
# Or on macOS:
brew install ollama

# Pull a model (recommended: llama3.2 or llama3.3)
ollama pull llama3.3

# Configure in config.json:
{
    "llm": {
        "model": "ollama/llama3.3",
        "api_base": "http://localhost:11434",
        "enabled": true
    }
}
```

#### Option 2: OpenAI API
```json
{
    "llm": {
        "model": "gpt-4o-mini",
        "api_base": "https://api.openai.com/v1",
        "enabled": true
    }
}
```
Set your API key: `export OPENAI_API_KEY="your-key-here"`

#### Option 3: Claude API
```json
{
    "llm": {
        "model": "claude-3-haiku-20240307",
        "api_base": "https://api.anthropic.com",
        "enabled": true
    }
}
```
Set your API key: `export ANTHROPIC_API_KEY="your-key-here"`

#### Option 4: Any Custom LLM Service
litellm supports 100+ LLM providers. See [litellm docs](https://docs.litellm.ai/docs/providers) for configuration examples.

### LLM Management Commands
```bash
# Show current LLM configuration
whenami --llm-config

# Test LLM connectivity with default query
whenami --llm-test

# Test with custom query
whenami --llm-test "busy next week"

# Get setup help and examples
whenami --llm-help
```

### Natural Language Examples

| Input | Converts To |
|-------|-------------|
| `"free tomorrow"` | `--tomorrow --free` |
| `"busy next week"` | `--next-week --busy` |
| `"work hours today"` | `--today --work-hours` |
| `"personal time on 15/07/25"` | `--date "15/07/25" --personal-hours` |
| `"show me August 2025"` | `--date-range "01/08/2025,31/08/2025"` |
| `"free weekdays next week"` | `--next-week --work-days --free` |
| `"tomorrow in New York time"` | `--tomorrow --convert-tz America/New_York` |
| `"today in Tokyo timezone"` | `--today --convert-tz Asia/Tokyo` |

The AI understands context, dates, time preferences, and complex queries, making calendar management more intuitive.

## Usage

### Natural Language Queries (Optional)
```bash
# Simple natural language - AI converts to appropriate commands (requires LLM setup)
whenami "free tomorrow"
whenami "busy next week"
whenami "work hours today"
whenami "personal time on 25/12/25"
whenami "show me next month"
whenami "tomorrow in New York time"
whenami "today in Tokyo timezone"

# Natural language with debug to see conversion
whenami "free tomorrow" --debug
```

### Traditional Command Line Options
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

# Custom dates (supports DD/MM/YYYY, DD/MM/YY, DD-MM-YYYY, DD-MM-YY)
whenami --date "25/12/2025"
whenami --date "25/12/25"
whenami --date "25-12-2025"

# Date ranges
whenami --date-range "01/08/2025,31/08/2025"
whenami --date-range "01/08/25,31/08/25"

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

The tool will automatically create a `~/.config/whenami/` directory for storing configuration files. You can place your configuration files there for system-wide access, or use the current directory for project-specific configurations.

1. Copy the example config file:
```bash
cp config.json.example ~/.config/whenami/config.json
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
- **`llm`**: **(Optional)** LLM configuration for natural language processing - disabled by default
  - **`model`**: Model to use (e.g., "ollama/llama3.3", "gpt-4o-mini", "claude-3-haiku-20240307")
  - **`api_base`**: LLM server endpoint (varies by provider, see setup examples above)
  - **`enabled`**: Enable/disable LLM features (false by default)

**📝 Note**: Add as many calendars as needed - the tool will merge all busy periods to show your true availability across all calendars. This is especially useful if you have separate work, personal, and project calendars that you need to coordinate.

The `default_timezone` setting controls the timezone used for date calculations (e.g., "today", "tomorrow"). If not specified, the tool will try to use your system's timezone, falling back to UTC.

## Authentication

The tool requires Google Calendar API authentication:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `credentials.json` in one of these locations:
   - `~/.config/whenami/credentials.json` (recommended for system-wide access)
   - `./credentials.json` (current directory, for project-specific setup)

The first time you run the tool, it will open a browser window for authentication. The authentication token will be saved in `~/.config/whenami/token.json` for future use.

## Development

This project uses GitHub Actions for CI/CD:

- **CI Pipeline**: Runs tests on Python 3.9-3.12, generates coverage reports, and validates builds
- **PyPI Publishing**: Automated publishing to PyPI on releases using trusted publishing

For development setup, see the [Local Development Setup](#local-development-setup) section above.
