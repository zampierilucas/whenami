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
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from whenami.utils.config import load_config

try:
    import litellm
except ImportError:
    litellm = None


def get_llm_config() -> Dict:
    """Load LLM configuration from config file"""
    config = load_config()
    return config.get('llm', {
        'model': 'ollama/llama3.3',
        'api_base': 'http://localhost:11434',
        'enabled': False
    })


def parse_with_llm(input_text: str, debug: bool = False) -> Optional[Dict]:
    """Parse text input using LLM and convert to command arguments"""
    if not litellm:
        print("[ERROR] litellm is not installed. Please install it to use LLM text processing.")
        return None

    config = get_llm_config()
    if not config.get('enabled', False):
        print("[ERROR] LLM features are disabled.")
        print("To enable natural language processing:")
        print("1. Add LLM configuration to config.json")
        print("2. Set 'enabled': true in the LLM section")
        print("3. Run 'whenami --llm-help' for setup instructions")
        return None

    # Use LLM processing for all natural language queries
    return _llm_process(input_text, config, debug=debug)




def _llm_process(text: str, config: Dict, debug: bool = False) -> Optional[Dict]:
    """Process text using LLM"""
    try:
        # Set up the LLM client
        litellm.api_base = config.get('api_base', 'http://100.118.13.153:11434')

        current_date = datetime.now().strftime("%Y-%m-%d")

        system_prompt = f"""You are a JSON generator. Convert calendar queries to JSON objects only.

Today: {current_date}

Rules:
- Calculate actual dates in DD/MM/YYYY format (today={current_date})
- "next week" = Monday-Sunday of next week
- Default to today if no date mentioned
- Use boolean true/false, not strings

Options: date, date_range, free, busy, work_hours, personal_hours, all_hours, work_days, split, event_name, convert_tz

Examples:
"free tomorrow" → {{"date": "12/07/2025", "free": true}}
"busy next week" → {{"date_range": "14/07/2025,20/07/2025", "busy": true}}
"work hours today" → {{"date": "11/07/2025", "work_hours": true}}
"next week nytime" → {{"date_range": "14/07/2025,20/07/2025", "convert_tz": "America/New_York"}}

ONLY return JSON, no explanations."""

        user_prompt = f"""Query: "{text}"

JSON Response:"""

        response = litellm.completion(
            model=config.get('model', 'ollama/llama3.3'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=100,
            stop=["\n\n", "```", "def ", "import "]
        )

        result_text = response.choices[0].message.content.strip()

        if debug:
            print(f"[LLM DEBUG] Raw LLM Response: {result_text}")

        # Clean up response - remove markdown formatting if present
        if result_text.startswith('```json'):
            result_text = result_text.replace('```json', '').replace('```', '').strip()

        # Try to parse JSON response
        try:
            result = json.loads(result_text)
            if 'error' in result:
                print(f"[ERROR] Could not parse: {result['error']}")
                return None
            return result
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON response from LLM: {result_text}")
            return None

    except Exception as e:
        print(f"[ERROR] LLM processing failed: {e}")
        return None


def convert_llm_to_args(llm_result: Dict) -> List[str]:
    """Convert LLM result dictionary to command line arguments"""
    args = []

    # Date options - LLM now provides explicit dates
    if llm_result.get('date'):
        args.extend(['--date', llm_result['date']])
    elif llm_result.get('date_range'):
        args.extend(['--date-range', llm_result['date_range']])
    else:
        # Default to today if no date specified
        current_date = datetime.now()
        date_str = current_date.strftime('%d/%m/%Y')
        args.extend(['--date', date_str])

    # Filter options
    if llm_result.get('free'):
        args.append('--free')
    elif llm_result.get('busy'):
        args.append('--busy')

    # Time options
    if llm_result.get('work_days'):
        args.append('--work-days')
    if llm_result.get('work_hours'):
        args.append('--work-hours')
    if llm_result.get('personal_hours'):
        args.append('--personal-hours')
    if llm_result.get('all_hours'):
        args.append('--all-hours')

    # Timezone conversion
    if llm_result.get('convert_tz'):
        args.extend(['--convert-tz', llm_result['convert_tz']])

    # Output options
    if llm_result.get('split'):
        args.append('--split')
    if llm_result.get('event_name'):
        args.append('--event-name')
    if llm_result.get('debug'):
        args.append('--debug')

    # These commands don't make sense for LLM processing since they're informational
    # --list-tz, --llm-config, --llm-test, --llm-help, --version, --help

    return args


def show_llm_config():
    """Show current LLM configuration"""
    config = get_llm_config()

    print("LLM Configuration:")
    print("=================")
    print(f"Enabled:   {config.get('enabled', True)}")
    print(f"Model:     {config.get('model', 'ollama/llama3.2')}")
    print(f"API Base:  {config.get('api_base', 'http://100.118.13.153:11434')}")
    print()

    # Check litellm availability
    if not litellm:
        print("❌ litellm is not installed")
        print("   Install with: pip install litellm")
    else:
        print("✅ litellm is installed")

    print()
    print("Configuration file: config.json")
    print("Edit the 'llm' section to modify settings.")


def test_llm(query: str):
    """Test LLM connectivity and parsing with a sample query"""
    print(f"Testing LLM with query: '{query}'")
    print("=" * 50)

    # Check prerequisites
    if not litellm:
        print("❌ litellm is not installed")
        print("   Install with: pip install litellm")
        return

    config = get_llm_config()
    if not config.get('enabled', True):
        print("❌ LLM processing is disabled in config")
        print("   Set 'enabled': true in config.json")
        return

    print(f"Using model: {config.get('model', 'ollama/llama3.2')}")
    print(f"API endpoint: {config.get('api_base', 'http://100.118.13.153:11434')}")
    print()

    # Test the parsing
    try:
        print("Sending query to LLM...")
        result = parse_with_llm(query)

        if result:
            print("✅ LLM Response:")
            print(f"   Raw result: {result}")

            # Convert to command line args
            args = convert_llm_to_args(result)
            print(f"   Command: whenami {' '.join(args)}")
            print()
            print("✅ Test successful! LLM is working correctly.")
        else:
            print("❌ LLM failed to parse the query")
            print("   Check your ollama server and model availability")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Ensure ollama is running on the configured endpoint")
        print("2. Check that the model is available (ollama list)")
        print("3. Verify network connectivity to the API endpoint")


def show_llm_help():
    """Show LLM usage instructions"""
    print("LLM Text Processing")
    print("===================")
    print()
    print("Usage:")
    print('  whenami "free tomorrow"')
    print('  whenami "busy next week"')
    print('  whenami "work hours on 15/07/25"')
    print('  whenami "free tomorrow" --debug    # Show LLM processing details')
    print()
    print("Configuration:")
    print("  --llm-config     Show current LLM settings")
    print("  --llm-test       Test LLM connectivity")
    print("  --llm-help       Show this help")
    print()
    print("Setup Instructions:")
    print("Option 1 - Local Ollama (Recommended):")
    print("1. Install ollama: https://ollama.ai")
    print("2. Pull a model: ollama pull llama3.3")
    print("3. Configure in config.json:")
    print('   {"llm": {"model": "ollama/llama3.3", "api_base": "http://localhost:11434", "enabled": true}}')
    print()
    print("Option 2 - OpenAI API:")
    print('   {"llm": {"model": "gpt-4o-mini", "api_base": "https://api.openai.com/v1", "enabled": true}}')
    print("   export OPENAI_API_KEY='your-key'")
    print()
    print("Option 3 - Claude API:")
    print('   {"llm": {"model": "claude-3-haiku-20240307", "api_base": "https://api.anthropic.com", "enabled": true}}')
    print("   export ANTHROPIC_API_KEY='your-key'")
    print()
    print("Note: litellm supports 100+ LLM providers - see https://docs.litellm.ai/docs/providers")
    print()
    print("Examples:")
    print('  "free tomorrow"                    -> --tomorrow --free')
    print('  "busy next week"                   -> --next-week --busy')
    print('  "work hours today"                 -> --today --work-hours')
    print('  "personal time on 15/07/25"        -> --date "15/07/25" --personal-hours')
    print('  "show me August 2025"              -> --date-range "01/08/2025,31/08/2025"')
    print('  "free tomorrow in NYC time"        -> --tomorrow --free --convert-tz "America/New_York"')
    print('  "busy today convert to UTC"        -> --today --busy --convert-tz "UTC"')
    print('  "show all hours today"             -> --today --all-hours')
    print('  "weekdays only next week"          -> --next-week --work-days')
    print('  "split free tomorrow with events" -> --tomorrow --free --split --event-name')
