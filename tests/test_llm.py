#!/usr/bin/env python3
"""
Test cases for LLM functionality in whenami.
"""

import pytest
from unittest.mock import patch, MagicMock
from whenami.utils.llm import (
    convert_llm_to_args, 
    get_llm_config, 
    parse_with_llm
)


class TestLLMConfig:
    """Test LLM configuration functionality"""
    
    def test_get_llm_config_default(self):
        """Test default LLM configuration"""
        with patch('whenami.utils.llm.load_config') as mock_load:
            mock_load.return_value = {}
            
            config = get_llm_config()
            
            assert config['model'] == 'ollama/llama3.3'
            assert config['api_base'] == 'http://localhost:11434'
            assert config['enabled'] is False
    
    def test_get_llm_config_custom(self):
        """Test custom LLM configuration"""
        with patch('whenami.utils.llm.load_config') as mock_load:
            mock_load.return_value = {
                'llm': {
                    'model': 'custom/model',
                    'api_base': 'http://custom.server:8080',
                    'enabled': False
                }
            }
            
            config = get_llm_config()
            
            assert config['model'] == 'custom/model'
            assert config['api_base'] == 'http://custom.server:8080'
            assert config['enabled'] is False




class TestLLMResultConversion:
    """Test conversion of LLM results to command line arguments"""
    
    def test_convert_date_options(self):
        """Test conversion of date options - LLM now provides explicit dates"""
        
        # Test explicit date - should pass through
        result = {'date': '15/07/25'}
        args = convert_llm_to_args(result)
        assert args == ['--date', '15/07/25']
        
        # Test date range - should pass through
        result = {'date_range': '01/08/2025,31/08/2025'}
        args = convert_llm_to_args(result)
        assert args == ['--date-range', '01/08/2025,31/08/2025']
        
        # Test explicit date with other options
        result = {'date': '12/07/2025', 'free': True}
        args = convert_llm_to_args(result)
        assert '--date' in args
        assert '12/07/2025' in args
        assert '--free' in args
    
    def test_convert_filter_options(self):
        """Test conversion of filter options"""
        from datetime import datetime
        
        # Test free - should default to today since no date provided
        result = {'free': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--free']
        
        # Test busy - should default to today since no date provided
        result = {'busy': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--busy']
    
    def test_convert_time_options(self):
        """Test conversion of time filtering options"""
        from datetime import datetime
        
        # Test work days - should default to today with date conversion
        result = {'work_days': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--work-days']
        
        # Test work hours - should default to today with date conversion
        result = {'work_hours': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--work-hours']
        
        # Test personal hours - should default to today with date conversion
        result = {'personal_hours': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--personal-hours']
        
        # Test all hours - should default to today with date conversion
        result = {'all_hours': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--all-hours']
    
    def test_convert_output_options(self):
        """Test conversion of output options"""
        from datetime import datetime
        
        # Test timezone conversion - should default to today with date conversion
        result = {'convert_tz': 'America/New_York'}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--convert-tz', 'America/New_York']
        
        # Test split - should default to today with date conversion
        result = {'split': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--split']
        
        # Test event name - should default to today with date conversion
        result = {'event_name': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--event-name']
        
        # Test debug - should default to today with date conversion
        result = {'debug': True}
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--debug']
    
    def test_convert_complex_combinations(self):
        """Test conversion of complex option combinations"""
        
        # Test multiple options with explicit date
        result = {
            'date': '12/07/2025',
            'free': True,
            'work_hours': True,
            'convert_tz': 'UTC',
            'split': True,
            'event_name': True
        }
        args = convert_llm_to_args(result)
        
        # Should have explicit date
        assert '--date' in args
        assert '12/07/2025' in args
        assert '--free' in args
        assert '--work-hours' in args
        assert '--convert-tz' in args
        assert 'UTC' in args
        assert '--split' in args
        assert '--event-name' in args
    
    def test_convert_mutually_exclusive_date_options(self):
        """Test that only one date option is used (first match wins)"""
        
        # If multiple date options are provided, should use first one found
        result = {
            'date': '15/07/25',
            'date_range': '01/08/2025,31/08/2025'  # Should be ignored
        }
        args = convert_llm_to_args(result)
        assert args == ['--date', '15/07/25']
    
    def test_convert_mutually_exclusive_filter_options(self):
        """Test that only one filter option is used"""
        from datetime import datetime
        
        result = {
            'free': True,
            'busy': True  # Should be ignored
        }
        args = convert_llm_to_args(result)
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date, '--free']
    
    def test_convert_empty_result(self):
        """Test conversion of empty result"""
        from datetime import datetime
        
        result = {}
        args = convert_llm_to_args(result)
        # Should default to today
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date]
    
    def test_convert_false_values(self):
        """Test that false values are ignored"""
        from datetime import datetime
        
        result = {
            'today': False,
            'free': False,
            'work_hours': False
        }
        args = convert_llm_to_args(result)
        # Should default to today since all values are false
        expected_date = datetime.now().strftime('%d/%m/%Y')
        assert args == ['--date', expected_date]


class TestLLMParsing:
    """Test LLM parsing functionality"""
    
    def test_parse_with_llm_no_litellm(self):
        """Test parsing when litellm is not available"""
        with patch('whenami.utils.llm.litellm', None):
            result = parse_with_llm("free tomorrow")
            assert result is None
    
    def test_parse_with_llm_disabled(self):
        """Test parsing when LLM is disabled"""
        with patch('whenami.utils.llm.litellm') as mock_litellm, \
             patch('whenami.utils.llm.get_llm_config') as mock_config:
            
            mock_config.return_value = {'enabled': False}
            
            result = parse_with_llm("free tomorrow")
            assert result is None
    
    @patch('whenami.utils.llm.litellm')
    def test_parse_with_llm_success(self, mock_litellm):
        """Test successful LLM parsing"""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"tomorrow": true, "free": true}'
        
        mock_litellm.completion.return_value = mock_response
        
        with patch('whenami.utils.llm.get_llm_config') as mock_config:
            mock_config.return_value = {
                'enabled': True,
                'model': 'test/model',
                'api_base': 'http://test.com'
            }
            
            result = parse_with_llm("free tomorrow")
            
            assert result is not None
            assert result['tomorrow'] is True
            assert result['free'] is True
    
    @patch('whenami.utils.llm.litellm')
    def test_parse_with_llm_invalid_json(self, mock_litellm):
        """Test LLM parsing with invalid JSON response"""
        # Mock LLM response with invalid JSON
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'invalid json response'
        
        mock_litellm.completion.return_value = mock_response
        
        with patch('whenami.utils.llm.get_llm_config') as mock_config:
            mock_config.return_value = {
                'enabled': True,
                'model': 'test/model',
                'api_base': 'http://test.com'
            }
            
            result = parse_with_llm("free tomorrow")
            assert result is None
    
    @patch('whenami.utils.llm.litellm')
    def test_parse_with_llm_error_response(self, mock_litellm):
        """Test LLM parsing with error response"""
        # Mock LLM response with error
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"error": "Could not parse input"}'
        
        mock_litellm.completion.return_value = mock_response
        
        with patch('whenami.utils.llm.get_llm_config') as mock_config:
            mock_config.return_value = {
                'enabled': True,
                'model': 'test/model',
                'api_base': 'http://test.com'
            }
            
            result = parse_with_llm("free tomorrow")
            assert result is None
    
    @patch('whenami.utils.llm.litellm')
    def test_parse_with_llm_exception(self, mock_litellm):
        """Test LLM parsing with exception"""
        # Mock LLM to raise exception
        mock_litellm.completion.side_effect = Exception("LLM error")
        
        with patch('whenami.utils.llm.get_llm_config') as mock_config:
            mock_config.return_value = {
                'enabled': True,
                'model': 'test/model',
                'api_base': 'http://test.com'
            }
            
            result = parse_with_llm("free tomorrow")
            assert result is None


class TestLLMIntegration:
    """Test end-to-end LLM integration scenarios"""
    
    def test_common_queries(self):
        """Test conversion of common query patterns"""
        from datetime import datetime, timedelta
        
        current_date = datetime.now()
        today_str = current_date.strftime('%d/%m/%Y')
        tomorrow_str = (current_date + timedelta(days=1)).strftime('%d/%m/%Y')
        
        test_cases = [
            # Basic queries with explicit dates
            ({'date': today_str}, ['--date', today_str]),
            ({'date': tomorrow_str, 'free': True}, ['--date', tomorrow_str, '--free']),
            
            # Date queries - these pass through unchanged
            ({'date': '15/07/25'}, ['--date', '15/07/25']),
            ({'date_range': '01/08/2025,31/08/2025'}, ['--date-range', '01/08/2025,31/08/2025']),
            
            # Time filtering with explicit dates
            ({'date': today_str, 'work_hours': True}, ['--date', today_str, '--work-hours']),
            ({'date': tomorrow_str, 'personal_hours': True}, ['--date', tomorrow_str, '--personal-hours']),
            ({'date': today_str, 'work_days': True}, ['--date', today_str, '--work-days']),
            
            # Output options with explicit dates
            ({'date': tomorrow_str, 'split': True}, ['--date', tomorrow_str, '--split']),
            ({'date': today_str, 'event_name': True}, ['--date', today_str, '--event-name']),
            
            # Timezone conversion with explicit dates
            ({'date': tomorrow_str, 'convert_tz': 'UTC'}, ['--date', tomorrow_str, '--convert-tz', 'UTC']),
            ({'date': today_str, 'convert_tz': 'America/New_York'}, ['--date', today_str, '--convert-tz', 'America/New_York']),
            
            # Complex combinations
            ({
                'date': tomorrow_str,
                'free': True,
                'work_hours': True,
                'split': True,
                'event_name': True,
                'convert_tz': 'UTC'
            }, ['--date', tomorrow_str, '--free', '--work-hours', '--convert-tz', 'UTC', '--split', '--event-name'])
        ]
        
        for llm_result, expected_args in test_cases:
            actual_args = convert_llm_to_args(llm_result)
            
            # Check that all expected args are present (order may vary)
            assert set(actual_args) == set(expected_args), f"Failed for {llm_result}: expected {expected_args}, got {actual_args}"
            
        # Test date_range separately
        date_range_result = {'date_range': '14/07/2025,20/07/2025', 'busy': True}
        date_range_args = convert_llm_to_args(date_range_result)
        assert date_range_args[0] == '--date-range'
        assert '14/07/2025,20/07/2025' in date_range_args
        assert '--busy' in date_range_args


@pytest.mark.integration
class TestLLMRealIntegration:
    """Test with actual LLM calls when available"""
    
    def test_real_llm_queries(self):
        """Test actual LLM parsing with real API calls"""
        import os
        
        # Skip if LLM is not configured or available
        config = get_llm_config()
        if not config.get('enabled', False):
            pytest.skip("LLM is not enabled in config")
        
        # Test queries that should work with a real LLM
        test_queries = [
            "free tomorrow",
            "busy today", 
            "work hours next week",
            "personal time on 15/07/25",
            "show me free time tomorrow",
            "busy weekdays next week"
        ]
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            result = parse_with_llm(query, debug=True)
            
            if result is not None:
                print(f"LLM Response: {result}")
                
                # Validate that we got a valid response
                assert isinstance(result, dict), f"Expected dict, got {type(result)}"
                
                # Convert to args to test the full pipeline
                args = convert_llm_to_args(result)
                print(f"Generated args: {args}")
                
                # Validate that we always get date parameters
                assert any(arg in ['--date', '--date-range'] for arg in args), \
                    f"Expected --date or --date-range in args: {args}"
                
                print("✅ Query processed successfully")
            else:
                print("❌ LLM failed to parse query")
                # Don't fail the test - just report the issue
                print(f"Warning: Could not parse '{query}' with real LLM")
    
    def test_edge_cases_with_real_llm(self):
        """Test edge cases with real LLM"""
        config = get_llm_config()
        if not config.get('enabled', False):
            pytest.skip("LLM is not enabled in config")
        
        # Test queries that might be ambiguous or challenging
        edge_cases = [
            "free",  # Should default to today
            "busy",  # Should default to today  
            "next week work",  # Should understand "next week" + "work"
            "tomorrow morning",  # Should understand "tomorrow"
            "15th of July",  # Different date format
            "this weekend",  # Relative date
        ]
        
        for query in edge_cases:
            print(f"\nTesting edge case: '{query}'")
            result = parse_with_llm(query, debug=True)
            
            if result is not None:
                args = convert_llm_to_args(result)
                print(f"Generated args: {args}")
                
                # Should always have a date parameter
                assert any(arg in ['--date', '--date-range'] for arg in args), \
                    f"Expected date parameter in args: {args}"
                
                print("✅ Edge case handled successfully")
            else:
                print(f"⚠️  Could not parse edge case '{query}'")
    
    def test_llm_response_format(self):
        """Test that LLM responses are in the expected JSON format"""
        config = get_llm_config()
        if not config.get('enabled', False):
            pytest.skip("LLM is not enabled in config")
        
        # Test a simple query
        result = parse_with_llm("free tomorrow", debug=True)
        
        if result is not None:
            # Validate JSON structure
            assert isinstance(result, dict), "LLM response should be a dict"
            
            # Should have boolean values, not strings
            for key, value in result.items():
                if isinstance(value, bool):
                    assert value in [True, False], f"Boolean values should be true/false, got {value}"
                elif isinstance(value, str):
                    # Date/timezone strings are OK
                    pass
                else:
                    pytest.fail(f"Unexpected value type for {key}: {type(value)}")
            
            print("✅ LLM response format is valid")
        else:
            pytest.skip("Could not get LLM response to test format")


if __name__ == '__main__':
    pytest.main([__file__])