import pytest
import argparse
from unittest.mock import patch, MagicMock
from whenami.main import main
import sys
from io import StringIO


class TestCLIArgumentParsing:
    """Test CLI argument parsing without requiring authentication or calendar access"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.original_argv = sys.argv.copy()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        sys.argv = self.original_argv
    
    def test_help_option(self):
        """Test that --help option works"""
        sys.argv = ['whenami', '--help']
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    
    def test_list_timezones_option(self):
        """Test --list-tz option"""
        sys.argv = ['whenami', '--list-tz']
        
        # Mock the list_timezones function and early exit
        with patch('whenami.main.list_timezones') as mock_list_tz, \
             patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            mock_list_tz.assert_called_once()
    
    @pytest.mark.parametrize("date_arg", [
        '--today',
        '--tomorrow', 
        '--next-week',
        '--next-two-weeks',
        '--date'
    ])
    def test_date_range_arguments(self, date_arg):
        """Test individual date range arguments"""
        sys.argv = ['whenami', date_arg]
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify that get_date_range was called with args containing the date option
            mock_date_range.assert_called_once()
            args, calendar_tz = mock_date_range.call_args[0]
            
            # Check that the correct date flag is set
            if date_arg == '--today':
                assert args.today is True
            elif date_arg == '--tomorrow':
                assert args.tomorrow is True
            elif date_arg == '--next-week':
                assert args.next_week is True
            elif date_arg == '--next-two-weeks':
                assert args.next_two_weeks is True
            elif date_arg == '--date':
                assert args.date == ''
    
    def test_mutually_exclusive_date_arguments(self):
        """Test that date range arguments are mutually exclusive"""
        sys.argv = ['whenami', '--today', '--tomorrow']
        
        # Should raise SystemExit due to mutually exclusive arguments
        with pytest.raises(SystemExit):
            main()
    
    @pytest.mark.parametrize("time_arg", [
        '--work-hours',
        '--personal-hours',
        '--all-hours'
    ])
    def test_time_filtering_arguments(self, time_arg):
        """Test time filtering arguments"""
        sys.argv = ['whenami', '--today', time_arg]
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify find_free_slots was called with correct args
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            args = call_args[1]['args']  # args is passed as keyword argument
            
            if time_arg == '--work-hours':
                assert args.work_hours is True
            elif time_arg == '--personal-hours':
                assert args.personal_hours is True
            elif time_arg == '--all-hours':
                assert args.all_hours is True
    
    def test_work_days_argument(self):
        """Test --work-days argument"""
        sys.argv = ['whenami', '--today', '--work-days']
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify find_free_slots was called with work_days flag
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            args = call_args[1]['args']
            assert args.work_days is True
    
    @pytest.mark.parametrize("output_arg", [
        '--free',
        '--busy'
    ])
    def test_output_format_arguments(self, output_arg):
        """Test output format arguments (--free, --busy)"""
        sys.argv = ['whenami', '--today', output_arg]
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify the show_free and show_busy flags are set correctly
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            args = call_args[1]['args']
            
            if output_arg == '--free':
                assert args.free is True
                assert args.show_free is True
                assert args.show_busy is False
            elif output_arg == '--busy':
                assert args.busy is True
                assert args.show_free is False
                assert args.show_busy is True
    
    def test_mutually_exclusive_output_arguments(self):
        """Test that --free and --busy are mutually exclusive"""
        sys.argv = ['whenami', '--free', '--busy']
        
        # Should raise SystemExit due to mutually exclusive arguments
        with pytest.raises(SystemExit):
            main()
    
    def test_split_argument(self):
        """Test --split argument"""
        sys.argv = ['whenami', '--today', '--split']
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify split=True is passed to find_free_slots
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            assert call_args[1]['split'] is True
    
    def test_convert_timezone_argument(self):
        """Test --convert-tz argument"""
        test_timezone = 'America/Sao_Paulo'
        sys.argv = ['whenami', '--today', '--convert-tz', test_timezone]
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify target_tz is passed correctly
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            assert call_args[1]['target_tz'] == test_timezone
    
    def test_debug_argument(self):
        """Test --debug argument"""
        sys.argv = ['whenami', '--today', '--debug']
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify debug flag is set
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            args = call_args[1]['args']
            assert args.debug is True
    
    def test_event_name_argument(self):
        """Test --event-name argument"""
        sys.argv = ['whenami', '--today', '--event-name']
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify event_name flag is set
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            args = call_args[1]['args']
            assert args.event_name is True
    
    def test_default_behavior_no_args(self):
        """Test default behavior when no arguments are provided"""
        sys.argv = ['whenami']
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify default behavior: both show_free and show_busy are True
            # (when neither --free nor --busy is specified)
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            args = call_args[1]['args']
            assert args.show_free is True
            assert args.show_busy is True
    
    def test_combined_arguments(self):
        """Test combination of multiple arguments"""
        sys.argv = ['whenami', '--next-week', '--work-days', '--work-hours', '--split', '--debug']
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            main()
            
            # Verify all arguments are set correctly
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            args = call_args[1]['args']
            
            assert args.next_week is True
            assert args.work_days is True
            assert args.work_hours is True
            assert args.debug is True
            assert call_args[1]['split'] is True


class TestArgumentValidation:
    """Test argument validation and error handling"""
    
    def test_invalid_timezone_format(self):
        """Test that invalid timezone format is handled gracefully"""
        # Note: The actual timezone validation happens in the calendar module
        # This test ensures the argument is parsed correctly
        sys.argv = ['whenami', '--today', '--convert-tz', 'InvalidTimezone']
        
        with patch('whenami.main.authenticate_google_calendar') as mock_auth, \
             patch('whenami.main.load_config') as mock_config, \
             patch('whenami.main.get_calendar_info') as mock_cal_info, \
             patch('whenami.main.get_timezone') as mock_tz, \
             patch('whenami.main.get_date_range') as mock_date_range, \
             patch('whenami.main.find_free_slots') as mock_find_slots:
            
            # Setup mocks
            mock_auth.return_value = MagicMock()
            mock_config.return_value = {'calendars': [{'id': 'test@example.com'}]}
            mock_cal_info.return_value = MagicMock()
            mock_tz.return_value = 'UTC'
            mock_date_range.return_value = ('2024-01-01', '2024-01-02')
            
            # Should not raise exception during argument parsing
            main()
            
            # Verify the invalid timezone is passed to find_free_slots
            # (validation happens there)
            mock_find_slots.assert_called_once()
            call_args = mock_find_slots.call_args
            assert call_args[1]['target_tz'] == 'InvalidTimezone'