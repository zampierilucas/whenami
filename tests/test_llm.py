#!/usr/bin/env python3
"""
Test cases for LLM functionality in whenami.
"""

import pytest
from unittest.mock import patch, MagicMock
from whenami.utils.llm import (
    convert_llm_to_args, 
    get_llm_config, 
    get_command_reference,
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


class TestCommandReference:
    """Test command reference generation"""
    
    def test_get_command_reference_success(self):
        """Test successful command reference generation"""
        # Mock subprocess to return help output
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "usage: whenami [options]\n\nOptions:\n  --today  Show today"
            mock_run.return_value = mock_result
            
            ref = get_command_reference()
            
            assert "WHENAMI COMMAND REFERENCE" in ref
            assert "usage: whenami [options]" in ref
            assert "ADDITIONAL EXAMPLES" in ref
    
    def test_get_command_reference_failure(self):
        """Test fallback when command reference generation fails"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Command failed")
            
            ref = get_command_reference()
            
            assert "WHENAMI COMMAND REFERENCE" in ref
            assert "Basic date options" in ref  # Fallback content


class TestLLMResultConversion:
    """Test conversion of LLM results to command line arguments"""
    
    def test_convert_date_options(self):
        """Test conversion of date options"""
        # Test today
        result = {'today': True}
        args = convert_llm_to_args(result)
        assert args == ['--today']
        
        # Test tomorrow
        result = {'tomorrow': True}
        args = convert_llm_to_args(result)
        assert args == ['--tomorrow']
        
        # Test next week
        result = {'next_week': True}
        args = convert_llm_to_args(result)
        assert args == ['--next-week']
        
        # Test next two weeks
        result = {'next_two_weeks': True}
        args = convert_llm_to_args(result)
        assert args == ['--next-two-weeks']
        
        # Test specific date
        result = {'date': '15/07/25'}
        args = convert_llm_to_args(result)
        assert args == ['--date', '15/07/25']
        
        # Test date range
        result = {'date_range': '01/08/2025,31/08/2025'}
        args = convert_llm_to_args(result)
        assert args == ['--date-range', '01/08/2025,31/08/2025']
    
    def test_convert_filter_options(self):
        """Test conversion of filter options"""
        # Test free
        result = {'free': True}
        args = convert_llm_to_args(result)
        assert args == ['--free']
        
        # Test busy
        result = {'busy': True}
        args = convert_llm_to_args(result)
        assert args == ['--busy']
    
    def test_convert_time_options(self):
        """Test conversion of time filtering options"""
        # Test work days
        result = {'work_days': True}
        args = convert_llm_to_args(result)
        assert args == ['--work-days']
        
        # Test work hours
        result = {'work_hours': True}
        args = convert_llm_to_args(result)
        assert args == ['--work-hours']
        
        # Test personal hours
        result = {'personal_hours': True}
        args = convert_llm_to_args(result)
        assert args == ['--personal-hours']
        
        # Test all hours
        result = {'all_hours': True}
        args = convert_llm_to_args(result)
        assert args == ['--all-hours']
    
    def test_convert_output_options(self):
        """Test conversion of output options"""
        # Test timezone conversion
        result = {'convert_tz': 'America/New_York'}
        args = convert_llm_to_args(result)
        assert args == ['--convert-tz', 'America/New_York']
        
        # Test split
        result = {'split': True}
        args = convert_llm_to_args(result)
        assert args == ['--split']
        
        # Test event name
        result = {'event_name': True}
        args = convert_llm_to_args(result)
        assert args == ['--event-name']
        
        # Test debug
        result = {'debug': True}
        args = convert_llm_to_args(result)
        assert args == ['--debug']
    
    def test_convert_complex_combinations(self):
        """Test conversion of complex option combinations"""
        # Test multiple options
        result = {
            'tomorrow': True,
            'free': True,
            'work_hours': True,
            'convert_tz': 'UTC',
            'split': True,
            'event_name': True
        }
        args = convert_llm_to_args(result)
        
        assert '--tomorrow' in args
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
            'today': True,
            'tomorrow': True,  # Should be ignored
            'next_week': True  # Should be ignored
        }
        args = convert_llm_to_args(result)
        assert args == ['--today']
    
    def test_convert_mutually_exclusive_filter_options(self):
        """Test that only one filter option is used"""
        result = {
            'free': True,
            'busy': True  # Should be ignored
        }
        args = convert_llm_to_args(result)
        assert args == ['--free']
    
    def test_convert_empty_result(self):
        """Test conversion of empty result"""
        result = {}
        args = convert_llm_to_args(result)
        assert args == []
    
    def test_convert_false_values(self):
        """Test that false values are ignored"""
        result = {
            'today': False,
            'free': False,
            'work_hours': False
        }
        args = convert_llm_to_args(result)
        assert args == []


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
        test_cases = [
            # Basic queries
            ({'today': True}, ['--today']),
            ({'tomorrow': True, 'free': True}, ['--tomorrow', '--free']),
            ({'next_week': True, 'busy': True}, ['--next-week', '--busy']),
            
            # Date queries
            ({'date': '15/07/25'}, ['--date', '15/07/25']),
            ({'date_range': '01/08/2025,31/08/2025'}, ['--date-range', '01/08/2025,31/08/2025']),
            
            # Time filtering
            ({'today': True, 'work_hours': True}, ['--today', '--work-hours']),
            ({'tomorrow': True, 'personal_hours': True}, ['--tomorrow', '--personal-hours']),
            ({'next_week': True, 'all_hours': True}, ['--next-week', '--all-hours']),
            ({'today': True, 'work_days': True}, ['--today', '--work-days']),
            
            # Output options
            ({'tomorrow': True, 'split': True}, ['--tomorrow', '--split']),
            ({'today': True, 'event_name': True}, ['--today', '--event-name']),
            
            # Timezone conversion
            ({'tomorrow': True, 'convert_tz': 'UTC'}, ['--tomorrow', '--convert-tz', 'UTC']),
            ({'today': True, 'convert_tz': 'America/New_York'}, ['--today', '--convert-tz', 'America/New_York']),
            
            # Complex combinations
            ({
                'tomorrow': True,
                'free': True,
                'work_hours': True,
                'split': True,
                'event_name': True,
                'convert_tz': 'UTC'
            }, ['--tomorrow', '--free', '--work-hours', '--convert-tz', 'UTC', '--split', '--event-name'])
        ]
        
        for llm_result, expected_args in test_cases:
            actual_args = convert_llm_to_args(llm_result)
            
            # Check that all expected args are present (order may vary)
            assert set(actual_args) == set(expected_args), f"Failed for {llm_result}: expected {expected_args}, got {actual_args}"


if __name__ == '__main__':
    pytest.main([__file__])