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
from datetime import datetime
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
        'model': 'ollama/llama3.2',
        'api_base': 'http://100.118.13.153:11434',
        'enabled': True
    })


def parse_with_llm(input_text: str, debug: bool = False) -> Optional[Dict]:
    """Parse text input using LLM and convert to command arguments"""
    if not litellm:
        print("[ERROR] litellm is not installed. Please install it to use LLM text processing.")
        return None

    config = get_llm_config()
    if not config.get('enabled', True):
        print("[ERROR] LLM processing is disabled in config.")
        return None

    # Use LLM processing for all natural language queries
    return _llm_process(input_text, config, debug=debug)


def get_command_reference() -> str:
    """Get complete command reference for LLM by executing --help"""
    import subprocess
    import sys
    import os

    try:
        # Get the path to the current module to find main.py
        current_dir = os.path.dirname(os.path.dirname(__file__))
        main_py_path = os.path.join(current_dir, 'main.py')

        # Run the help command
        result = subprocess.run(
            [sys.executable, main_py_path, '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            help_output = result.stdout

            # Add a header and some examples for better LLM understanding
            command_ref = f"""WHENAMI COMMAND REFERENCE:

{help_output}

ADDITIONAL EXAMPLES FOR NATURAL LANGUAGE PARSING:
  "free tomorrow" -> --tomorrow --free
  "busy next week" -> --next-week --busy
  "work hours today" -> --today --work-hours
  "personal time on 15/07/25" -> --date "15/07/25" --personal-hours
  "show me August 2025" -> --date-range "01/08/2025,31/08/2025"
  "free weekdays next week" -> --next-week --work-days --free
"""
            return command_ref
        else:
            # Fallback if help command fails
            return _get_fallback_command_reference()

    except Exception:
        # Fallback if subprocess fails
        return _get_fallback_command_reference()


def _get_fallback_command_reference() -> str:
    """Fallback command reference if --help extraction fails"""
    return """
WHENAMI COMMAND REFERENCE:

Basic date options: --today, --tomorrow, --next-week, --next-two-weeks
Custom dates: --date "DD/MM/YYYY" or --date-range "start,end"
Time filters: --work-hours, --personal-hours, --all-hours, --work-days
Display: --free, --busy, --split, --event-name
Output: --convert-tz, --list-tz, --debug

Examples:
  "free tomorrow" -> --tomorrow --free
  "busy next week" -> --next-week --busy
  "work hours on 15/07/25" -> --date "15/07/25" --work-hours
"""


def _llm_process(text: str, config: Dict, debug: bool = False) -> Optional[Dict]:
    """Process text using LLM"""
    try:
        # Set up the LLM client, by default try local ollama server
        litellm.api_base = config.get('api_base', 'http://localhost:11434')

        command_ref = get_command_reference()
        current_date = datetime.now().strftime("%Y-%m-%d")

        system_prompt = f"""You are a JSON response generator. Convert natural language calendar queries to JSON objects.

Today's date: {current_date}

{command_ref}

CRITICAL: You must respond with ONLY a JSON object. Do not write code, explanations, or anything else.

JSON RULES:
- Use boolean true/false (not strings)
- Date format: DD/MM/YYYY or DD/MM/YY
- Date ranges: "start,end" format
- Calculate dates from today: {current_date}

EXAMPLES:
Input: "free tomorrow"
Output: {{"tomorrow": true, "free": true}}

Input: "busy next week"
Output: {{"next_week": true, "busy": true}}

Input: "work hours today"
Output: {{"today": true, "work_hours": true}}

Input: "on 15/07/25"
Output: {{"date": "15/07/25"}}

RESPOND WITH JSON ONLY - NO CODE, NO EXPLANATIONS."""

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

    # Date options (mutually exclusive)
    if llm_result.get('today'):
        args.append('--today')
    elif llm_result.get('tomorrow'):
        args.append('--tomorrow')
    elif llm_result.get('next_week'):
        args.append('--next-week')
    elif llm_result.get('next_two_weeks'):
        args.append('--next-two-weeks')
    elif llm_result.get('date'):
        args.extend(['--date', llm_result['date']])
    elif llm_result.get('date_range'):
        args.extend(['--date-range', llm_result['date_range']])

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
    print('  "free tomorrow"              -> --tomorrow --free')
    print('  "busy next week"             -> --next-week --busy')
    print('  "work hours today"           -> --today --work-hours')
    print('  "personal time on 15/07/25"  -> --date "15/07/25" --personal-hours')
    print('  "show me August 2025"        -> --date-range "01/08/2025,31/08/2025"')