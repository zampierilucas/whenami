import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from whenami.utils.calendar import TimeSlot, organize_slots, merge_busy_periods, display_slots


class TestEventNames:
    """Test event name functionality"""
    
    def test_timeslot_with_event_name(self):
        """Test TimeSlot creation with event name"""
        start = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        
        slot = TimeSlot(start=start, end=end, is_busy=True, event_name="Meeting")
        
        assert slot.start == start
        assert slot.end == end
        assert slot.is_busy is True
        assert slot.event_name == "Meeting"
    
    def test_timeslot_without_event_name(self):
        """Test TimeSlot creation without event name"""
        start = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        
        slot = TimeSlot(start=start, end=end, is_busy=False)
        
        assert slot.start == start
        assert slot.end == end
        assert slot.is_busy is False
        assert slot.event_name is None
    
    def test_organize_slots_with_event_names(self):
        """Test organize_slots function with event names"""
        start_date = datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 1, 18, 0, tzinfo=timezone.utc)
        tz = ZoneInfo("UTC")
        
        busy_times = [
            ("2024-01-01T09:00:00Z", "2024-01-01T10:00:00Z", "Morning Meeting"),
            ("2024-01-01T14:00:00Z", "2024-01-01T15:00:00Z", "Afternoon Call")
        ]
        
        slots = organize_slots(busy_times, start_date, end_date, tz)
        
        # Should have 5 slots: free, busy, free, busy, free
        assert len(slots) == 5
        
        # Check first free slot
        assert slots[0].is_busy is False
        assert slots[0].event_name is None
        
        # Check first busy slot
        assert slots[1].is_busy is True
        assert slots[1].event_name == "Morning Meeting"
        
        # Check second free slot
        assert slots[2].is_busy is False
        assert slots[2].event_name is None
        
        # Check second busy slot
        assert slots[3].is_busy is True
        assert slots[3].event_name == "Afternoon Call"
        
        # Check final free slot
        assert slots[4].is_busy is False
        assert slots[4].event_name is None
    
    def test_organize_slots_without_event_names(self):
        """Test organize_slots function without event names"""
        start_date = datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 1, 18, 0, tzinfo=timezone.utc)
        tz = ZoneInfo("UTC")
        
        busy_times = [
            ("2024-01-01T09:00:00Z", "2024-01-01T10:00:00Z", None),
            ("2024-01-01T14:00:00Z", "2024-01-01T15:00:00Z", None)
        ]
        
        slots = organize_slots(busy_times, start_date, end_date, tz)
        
        # Should have 5 slots: free, busy, free, busy, free
        assert len(slots) == 5
        
        # Check busy slots have no event names
        assert slots[1].is_busy is True
        assert slots[1].event_name is None
        assert slots[3].is_busy is True
        assert slots[3].event_name is None
    
    def test_merge_busy_periods_with_event_names(self):
        """Test merge_busy_periods with event names"""
        busy_periods_list = [
            [
                {"start": "2024-01-01T09:00:00Z", "end": "2024-01-01T10:00:00Z", "summary": "Meeting A"},
                {"start": "2024-01-01T11:00:00Z", "end": "2024-01-01T12:00:00Z", "summary": "Meeting B"}
            ],
            [
                {"start": "2024-01-01T09:30:00Z", "end": "2024-01-01T10:30:00Z", "summary": "Overlapping Call"}
            ]
        ]
        
        merged = merge_busy_periods(busy_periods_list)
        
        # Should have 2 periods: merged overlapping one and standalone one
        assert len(merged) == 2
        
        # Check first merged period
        assert merged[0]["start"] == "2024-01-01T09:00:00Z"
        assert merged[0]["end"] == "2024-01-01T10:30:00Z"
        assert merged[0]["summary"] == "Meeting A / Overlapping Call"
        
        # Check second period
        assert merged[1]["start"] == "2024-01-01T11:00:00Z"
        assert merged[1]["end"] == "2024-01-01T12:00:00Z"
        assert merged[1]["summary"] == "Meeting B"
    
    def test_merge_busy_periods_without_event_names(self):
        """Test merge_busy_periods without event names"""
        busy_periods_list = [
            [
                {"start": "2024-01-01T09:00:00Z", "end": "2024-01-01T10:00:00Z", "summary": None},
                {"start": "2024-01-01T11:00:00Z", "end": "2024-01-01T12:00:00Z", "summary": None}
            ]
        ]
        
        merged = merge_busy_periods(busy_periods_list)
        
        assert len(merged) == 2
        assert merged[0]["summary"] is None
        assert merged[1]["summary"] is None
    
    def test_merge_busy_periods_mixed_event_names(self):
        """Test merge_busy_periods with some events having names and others not"""
        busy_periods_list = [
            [
                {"start": "2024-01-01T09:00:00Z", "end": "2024-01-01T10:00:00Z", "summary": "Named Event"},
                {"start": "2024-01-01T09:30:00Z", "end": "2024-01-01T10:30:00Z", "summary": None}
            ]
        ]
        
        merged = merge_busy_periods(busy_periods_list)
        
        assert len(merged) == 1
        assert merged[0]["summary"] == "Named Event"
    
    @patch('builtins.print')
    def test_display_slots_with_event_names(self, mock_print):
        """Test display_slots function with event names enabled"""
        # Create mock args with event_name enabled
        args = MagicMock()
        args.event_name = True
        args.show_free = True
        args.show_busy = True
        
        # Create test slots
        start1 = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
        end1 = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        start2 = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        end2 = datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc)
        
        slots = [
            TimeSlot(start=start1, end=end1, is_busy=True, event_name="Important Meeting"),
            TimeSlot(start=start2, end=end2, is_busy=False, event_name=None)
        ]
        
        with patch('whenami.utils.calendar.load_config') as mock_config, \
             patch('whenami.utils.calendar.get_work_hours') as mock_work_hours:
            
            mock_config.return_value = {}
            mock_work_hours.return_value = ("09:00", "17:00", None, None)
            
            display_slots(slots, args=args)
            
            # Verify that print was called with event name for busy slot
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            busy_call_found = False
            for call in print_calls:
                if "Important Meeting" in call:
                    busy_call_found = True
                    break
            
            assert busy_call_found, "Event name should be displayed for busy slots"
    
    @patch('builtins.print')
    def test_display_slots_without_event_names(self, mock_print):
        """Test display_slots function with event names disabled"""
        # Create mock args with event_name disabled
        args = MagicMock()
        args.event_name = False
        args.show_free = True
        args.show_busy = True
        
        # Create test slots
        start1 = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
        end1 = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        
        slots = [
            TimeSlot(start=start1, end=end1, is_busy=True, event_name="Important Meeting")
        ]
        
        with patch('whenami.utils.calendar.load_config') as mock_config, \
             patch('whenami.utils.calendar.get_work_hours') as mock_work_hours:
            
            mock_config.return_value = {}
            mock_work_hours.return_value = ("09:00", "17:00", None, None)
            
            display_slots(slots, args=args)
            
            # Verify that event name is not displayed when flag is disabled
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            for call in print_calls:
                assert "Important Meeting" not in call, "Event name should not be displayed when flag is disabled"