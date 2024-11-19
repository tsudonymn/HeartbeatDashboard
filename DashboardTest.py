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
        heartbeat = HeartBeat(device_id ="Patrick", timestamp = datetime.now(tz=timezone.utc))
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        frame = dash.generateViewFrame().to_dict(orient='records')

        data = [{'device_id': 'Patrick', 'uptime': 100}]

        expected = pd.DataFrame(data).to_dict(orient='records')

        assert_that(frame).is_equal_to(expected)

    def test_calc_uptime(self):
        interval = 10
        window = 30
        now = datetime.now(tz=timezone.utc)
        dash = DashBoard(heartbeat_interval=interval, uptime_window=window)
        heartbeat = HeartBeat("Patrick", now)
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())

        uptime = dash.calculateUptime("Patrick", now + timedelta(seconds=20))

        assert_that(uptime).is_equal_to(100)


    def test_expected_heartbeats(self):
        interval = 10
        window = 60
        dash = DashBoard(heartbeat_interval=interval, uptime_window=window)

        assert_that(dash.calculate_expected_number_of_heartbeats(interval, window)).is_equal_to(6)

    def test_calc_uptime2(self):
        interval = 10
        window = 60
        now = datetime.now(tz=timezone.utc)
        dash = DashBoard(heartbeat_interval=interval, uptime_window=window)

        heartbeat = HeartBeat("Patrick", now)
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())

        uptime = dash.calculateUptime("Patrick", now + timedelta(seconds=60))

        assert_that(uptime).is_equal_to(100)


    def test_calc_uptime_intermittent(self):
        interval = 10
        window = 60
        now = datetime.now(tz=timezone.utc)
        dash = DashBoard(heartbeat_interval=interval, uptime_window=window)

        heartbeat = HeartBeat("Patrick", now)
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())

        uptime = dash.calculateUptime("Patrick", now + timedelta(seconds=60))

        assert_that(uptime).is_equal_to(83)

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

    def test_get_heartbeats_in_window(self):
        dash = DashBoard()
        now = datetime.now(tz=timezone.utc)
        
        # Create heartbeats at different times
        heartbeats = [
            HeartBeat("Device1", now - timedelta(seconds=100)),  # too old
            HeartBeat("Device1", now - timedelta(seconds=50)),   # in window
            HeartBeat("Device1", now - timedelta(seconds=25)),   # in window
            HeartBeat("Device1", now),                           # in window
            HeartBeat("Device1", now + timedelta(seconds=10)),   # future
            HeartBeat("Device2", now - timedelta(seconds=50))    # different device
        ]
        
        # Add all heartbeats to dashboard
        for hb in heartbeats:
            dash.addHeartBeat(hb)
        
        # Get heartbeats in a 60-second window
        window_start = now - timedelta(seconds=60)
        filtered_heartbeats = dash.get_heartbeats_in_window("Device1", window_start, now)
        
        # Should only include the 3 heartbeats within the window for Device1
        assert_that(len(filtered_heartbeats)).is_equal_to(3)
        
        # Verify each heartbeat is within the window
        for hb in filtered_heartbeats:
            assert_that(hb.device_id).is_equal_to("Device1")
            assert_that(hb.timestamp).is_greater_than_or_equal_to(window_start)
            assert_that(hb.timestamp).is_less_than_or_equal_to(now)
            
        # Test with no heartbeats in window
        empty_window_start = now + timedelta(seconds=100)
        empty_window_end = now + timedelta(seconds=200)
        empty_result = dash.get_heartbeats_in_window("Device1", empty_window_start, empty_window_end)
        assert_that(empty_result).is_empty()
        
        # Test with unknown device
        unknown_result = dash.get_heartbeats_in_window("UnknownDevice", window_start, now)
        assert_that(unknown_result).is_empty()

    def test_given_a_time_interval_and_matching_heartbeat_data_we_get_right_heartbeats(self):
        dash = DashBoard(heartbeat_interval=10, uptime_window=40)
        heartbeat = HeartBeat(device_id="Patrick", timestamp=datetime.now(tz=timezone.utc))
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        
        # Get heartbeats between first and last timestamp
        actual_heartbeats = dash.get_heartbeats_in_window(
            "Patrick", 
            heartbeat.timestamp, 
            heartbeat.timestamp + timedelta(seconds=30)
        )

        # Should find 4 heartbeats (at 0s, 10s, 20s, and 30s)
        assert_that(len(actual_heartbeats)).is_equal_to(4)
        
        # # Verify timestamps are sequential
        # for i in range(len(actual_heartbeats) - 1):
        #     time_diff = actual_heartbeats[i + 1].timestamp - actual_heartbeats[i].timestamp
        #     assert_that(time_diff.total_seconds()).is_equal_to(10)

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


if __name__ == '__main__':
    unittest.main()
