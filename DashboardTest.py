import unittest
from datetime import datetime, timezone, timedelta

import pandas as pd
from assertpy import assert_that

from Dashboard import DashBoard
from DeviceDashboardViewRow import DeviceDashboardViewRow
from Heartbeat import HeartBeat

initial_timestamp = datetime.now()

data = [
    {
        'device': 'Patrick',
        'timestamp': initial_timestamp
    },
    {
        'device': 'Patrick',
        'timestamp': initial_timestamp + timedelta(seconds=10)
    },
    {
        'device': 'Patrick',
        'timestamp': initial_timestamp + timedelta(seconds=20)
    }
]

THE_100_FRAME = pd.DataFrame(data)

initial_timestamp = datetime.now()

data = [
    {
        'device': 'Patrick',
        'timestamp': initial_timestamp
    },
    {
        'device': 'Patrick',
        'timestamp': initial_timestamp + timedelta(seconds=20)
    }
]

THE_INTERMITTENT_FRAME = pd.DataFrame(data)

initial_timestamp = datetime.now()

data = [
    {
        'device': 'Patrick',
        'timestamp': initial_timestamp
    },
    {
        'device': 'Patrick',
        'timestamp': initial_timestamp + timedelta(seconds=10)
    },
]

# Create the DataFrame
THE_DEAD_FRAME = pd.DataFrame(data)


class MyTestCase(unittest.TestCase):
    def test_uptime_default_to_beginning_of_time(self):
        device = DeviceDashboardViewRow(' ')
        assert_that(device.uptime).is_equal_to(0)  # add assertion here

    def test_given_datetime_you_get_time_set(self):
        nownow = datetime.now(tz=timezone.utc)
        device = DeviceDashboardViewRow(' ', uptime=nownow)
        assert_that(device.uptime).is_equal_to(nownow)

    def test_given_a_time_interval_and_matching_heartbeat_data_we_calc_100_uptime_correctly(self):
        dash = DashBoard(heartbeat_interval=10, uptime_window=40)
        heartbeat = HeartBeat(device_id="Patrick", timestamp=datetime.now(tz=timezone.utc))
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        frame = dash.generateViewFrame().to_dict(orient='records')

        data = [{'device_id': 'Patrick', 'uptime': 100}]

        expected = pd.DataFrame(data).to_dict(orient='records')

        assert_that(frame).is_equal_to(expected)

    def test_calc_uptime(self):
        """Test uptime calculation with aligned intervals"""
        interval = 10
        window = 30
        base_time = datetime(2024, 1, 1, 1, 0, tzinfo=timezone.utc)
        dash = DashBoard(heartbeat_interval=interval, uptime_window=window)
        
        # Create heartbeats at 1:00, 1:10, 1:20
        heartbeats = [
            HeartBeat("Device1", base_time),
            HeartBeat("Device1", base_time + timedelta(seconds=10)),
            HeartBeat("Device1", base_time + timedelta(seconds=20))
        ]
        
        for hb in heartbeats:
            dash.addHeartBeat(hb)
        
        # Case 1: Calculate uptime at 1:20 (aligned with interval)
        # Window: 0:50 to 1:20 (30 seconds)
        # Expected heartbeats: 4 (0:50, 1:00, 1:10, 1:20)
        # Actual heartbeats: 3 (1:00, 1:10, 1:20)
        uptime = dash.calculateUptime("Device1", base_time + timedelta(seconds=20))
        assert_that(uptime).described_as("Uptime at aligned time (1:20)").is_equal_to(75)  # 3/4 = 75%
        
        # Case 2: Calculate uptime at 1:21 (not aligned)
        # Window: 0:51 to 1:21 (30 seconds)
        # Expected heartbeats: 3 (1:00, 1:10, 1:20)
        # Actual heartbeats: 3 (1:00, 1:10, 1:20)
        uptime = dash.calculateUptime("Device1", base_time + timedelta(seconds=21))
        assert_that(uptime).described_as("Uptime at non-aligned time (1:21)").is_equal_to(100)  # 3/3 = 100%

    def test_given_a_time_interval_and_matching_heartbeat_data_we_calc_uptime_correctly(self):
        dash = DashBoard(heartbeat_interval=10, uptime_window=40)
        heartbeat = HeartBeat(device_id="Patrick", timestamp=datetime.now(tz=timezone.utc))
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        frame = dash.generateViewFrame().to_dict(orient='records')

        data = [{'device_id': 'Patrick', 'uptime': 100}]

        expected = pd.DataFrame(data).to_dict(orient='records')

        assert_that(frame).is_equal_to(expected)

    def test_expected_heartbeats(self):
        """Test the calculation of expected heartbeats with different window sizes"""
        dash = DashBoard(heartbeat_interval=10)
        
        # Case 1: Window aligned with interval (30 seconds)
        assert_that(dash.calculate_expected_number_of_heartbeats(10, 30)).described_as(
            "30s window (aligned)").is_equal_to(4)  # at 0s, 10s, 20s, 30s
            
        # Case 2: Window not aligned with interval (35 seconds)
        assert_that(dash.calculate_expected_number_of_heartbeats(10, 35)).described_as(
            "35s window (not aligned)").is_equal_to(3)  # at 0s, 10s, 20s (30s is incomplete)
            
        # Case 3: Exact single interval
        assert_that(dash.calculate_expected_number_of_heartbeats(10, 10)).described_as(
            "10s window").is_equal_to(2)  # at 0s and 10s

    def test_heartbeats_filtered_by_time_window(self):
        """Test heartbeat filtering with different window alignments"""
        dash = DashBoard(heartbeat_interval=10, uptime_window=30)
        base_time = datetime(2024, 1, 1, 1, 0, tzinfo=timezone.utc)
        
        # Create heartbeats at 1:00, 1:10, 1:20, 1:30
        heartbeats = [
            HeartBeat("Device1", base_time),                           # 1:00
            HeartBeat("Device1", base_time + timedelta(minutes=10)),   # 1:10
            HeartBeat("Device1", base_time + timedelta(minutes=20)),   # 1:20
            HeartBeat("Device1", base_time + timedelta(minutes=30)),   # 1:30
        ]
        
        for hb in heartbeats:
            dash.addHeartBeat(hb)
            
        # Case 1: Window aligned with interval (1:30)
        now = base_time + timedelta(minutes=30)  # 1:30
        uptime = dash.calculateUptime("Device1", now)
        assert_that(uptime).described_as("Uptime at 1:30 (aligned)").is_equal_to(100)
        
        # Case 2: Window not aligned with interval (1:31)
        now = base_time + timedelta(minutes=30, seconds=1)  # 1:31
        uptime = dash.calculateUptime("Device1", now)
        assert_that(uptime).described_as("Uptime at 1:31 (not aligned)").is_equal_to(100)
        
        # Case 3: Window starting between intervals (1:25)
        now = base_time + timedelta(minutes=25)  # 1:25
        uptime = dash.calculateUptime("Device1", now)
        assert_that(uptime).described_as("Uptime at 1:25 (mid-interval)").is_equal_to(100)

    def test_get_heartbeats_in_window(self):
        """Test getting heartbeats within specific time windows"""
        dash = DashBoard(heartbeat_interval=10)
        base_time = datetime(2024, 1, 1, 1, 0, tzinfo=timezone.utc)
        
        # Create heartbeats at 1:00, 1:10, 1:20
        heartbeats = [
            HeartBeat("Device1", base_time),                           # 1:00
            HeartBeat("Device1", base_time + timedelta(minutes=10)),   # 1:10
            HeartBeat("Device1", base_time + timedelta(minutes=20)),   # 1:20
        ]
        
        for hb in heartbeats:
            dash.addHeartBeat(hb)
            
        # Case 1: Window aligned with interval
        window_end = base_time + timedelta(minutes=20)  # 1:20
        window_start = window_end - timedelta(seconds=30)
        filtered = dash.get_heartbeats_in_window("Device1", window_start, window_end)
        assert_that(len(filtered)).described_as(
            "Heartbeats in aligned window").is_equal_to(3)  # 1:00, 1:10, 1:20
            
        # Case 2: Window not aligned with interval
        window_end = base_time + timedelta(minutes=20, seconds=1)  # 1:20:01
        window_start = window_end - timedelta(seconds=30)
        filtered = dash.get_heartbeats_in_window("Device1", window_start, window_end)
        assert_that(len(filtered)).described_as(
            "Heartbeats in non-aligned window").is_equal_to(2)  # 1:10, 1:20

    def test_calc_uptime2(self):
        """Test uptime calculation with longer window"""
        interval = 10
        window = 30  # Changed from 60 to 30 for clarity
        base_time = datetime(2024, 1, 1, 1, 0, tzinfo=timezone.utc)
        dash = DashBoard(heartbeat_interval=interval, uptime_window=window)
        
        # Create heartbeats every 10 seconds from 1:00 to 1:20
        heartbeats = []
        for i in range(3):  # 1:00, 1:10, 1:20
            hb_time = base_time + timedelta(seconds=i*10)
            heartbeats.append(HeartBeat("Device1", hb_time))
        
        for hb in heartbeats:
            dash.addHeartBeat(hb)
        
        # Calculate uptime at 1:20 (aligned with interval)
        # Window: 0:50 to 1:20 (30 seconds)
        # Expected heartbeats: 4 (0:50, 1:00, 1:10, 1:20)
        # Actual heartbeats: 3 (1:00, 1:10, 1:20)
        uptime = dash.calculateUptime("Device1", base_time + timedelta(seconds=20))
        assert_that(uptime).described_as("Uptime at 1:20").is_equal_to(75)  # 3/4 = 75%

    def test_calc_uptime_intermittent(self):
        """Test uptime calculation with missing heartbeats"""
        interval = 10
        window = 30
        base_time = datetime(2024, 1, 1, 1, 0, tzinfo=timezone.utc)
        dash = DashBoard(heartbeat_interval=interval, uptime_window=window)
        
        # Create heartbeats at 1:00 and 1:10 (missing 1:20)
        heartbeats = [
            HeartBeat("Device1", base_time),
            HeartBeat("Device1", base_time + timedelta(seconds=10))
        ]
        
        for hb in heartbeats:
            dash.addHeartBeat(hb)
        
        # Calculate uptime at 1:20 (aligned with interval)
        # Window: 0:50 to 1:20 (30 seconds)
        # Expected heartbeats: 4 (0:50, 1:00, 1:10, 1:20)
        # Actual heartbeats: 2 (1:00, 1:10)
        now = base_time + timedelta(seconds=20)
        uptime = dash.calculateUptime("Device1", now)
        assert_that(uptime).described_as("Uptime with missing heartbeat").is_equal_to(50)  # 2/4 = 50%

    def test_heartbeats_filtered_by_time_window(self):
        # Setup dashboard with 10 second interval and 30 second window
        dash = DashBoard(heartbeat_interval=10, uptime_window=30)

        # Create a fixed reference time
        now = datetime.now(tz=timezone.utc)

        # Add heartbeats at different times:
        # - One before the window (should be excluded)
        # - Three within the window (should be included)
        # - One after the window (should be excluded)
        heartbeats = [
            HeartBeat("Patrick", now - timedelta(seconds=40)),  # too old
            HeartBeat("Patrick", now - timedelta(seconds=20)),  # in window
            HeartBeat("Patrick", now - timedelta(seconds=10)),  # in window
            HeartBeat("Patrick", now),                          # in window
            HeartBeat("Patrick", now + timedelta(seconds=10))   # future
        ]

        for hb in heartbeats:
            dash.addHeartBeat(hb)

        # Calculate uptime at the reference time
        uptime = dash.calculateUptime("Patrick", now)

        # With 10s interval and 30s window, we expect 4 heartbeats
        # We have 3 heartbeats in the window, so uptime should be 75%
        assert_that(uptime).is_equal_to(75)

    def test_is_in_window(self):
        dash = DashBoard()
        now = datetime.now(tz=timezone.utc)
        window_start = now - timedelta(seconds=60)
        window_end = now

        # Test timestamp at window start (should be included)
        assert_that(dash.is_in_window(window_start, window_start, window_end)).is_true()

        # Test timestamp at window end (should be included)
        assert_that(dash.is_in_window(window_end, window_start, window_end)).is_true()

        # Test timestamp in middle of window (should be included)
        middle_time = now - timedelta(seconds=30)
        assert_that(dash.is_in_window(middle_time, window_start, window_end)).is_true()

        # Test timestamp before window (should be excluded)
        before_window = window_start - timedelta(seconds=1)
        assert_that(dash.is_in_window(before_window, window_start, window_end)).is_false()

        # Test timestamp after window (should be excluded)
        after_window = window_end + timedelta(seconds=1)
        assert_that(dash.is_in_window(after_window, window_start, window_end)).is_false()

        # Test with zero-length window (single point in time)
        point_in_time = now
        assert_that(dash.is_in_window(point_in_time, point_in_time, point_in_time)).is_true()

    def test_heartbeat_counting_with_interval_alignment(self):
        """Test heartbeat counting with different current time alignments."""
        # Create a fixed base time at 1:30
        base_time = datetime(2024, 1, 1, 1, 30, tzinfo=timezone.utc)

        # Create heartbeats at 1:30, 1:40, and 1:50
        heartbeats = [
            HeartBeat("Device1", base_time),                           # 1:30
            HeartBeat("Device1", base_time + timedelta(minutes=10)),   # 1:40
            HeartBeat("Device1", base_time + timedelta(minutes=20)),   # 1:50
        ]

        dash = DashBoard(heartbeat_interval=10, uptime_window=30)
        for hb in heartbeats:
            dash.addHeartBeat(hb)

        # Test Case 1: now = 2:01 (not aligned with interval)
        now = base_time + timedelta(minutes=31)  # 2:01
        uptime = dash.calculateUptime("Device1", now)
        # We expect 2 heartbeats (1:40 and 1:50) in a 30s window from 1:31 to 2:01
        assert_that(uptime).described_as("Uptime at 2:01").is_equal_to(67)  # 2/3 ≈ 67%

        # Test Case 2: now = 2:00 (aligned with interval)
        now = base_time + timedelta(minutes=30)  # 2:00
        uptime = dash.calculateUptime("Device1", now)
        # We expect 3 heartbeats (1:40, 1:50, and potential 2:00) in a 30s window from 1:30 to 2:00
        assert_that(uptime).described_as("Uptime at 2:00").is_equal_to(100)  # 3/3 = 100%


if __name__ == '__main__':
    unittest.main()
