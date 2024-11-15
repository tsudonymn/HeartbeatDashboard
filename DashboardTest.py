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
        assert_that(device.uptime).is_equal_to(datetime.fromtimestamp(0, tz=timezone.utc))  # add assertion here

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


if __name__ == '__main__':
    unittest.main()
