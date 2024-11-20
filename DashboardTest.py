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
        heartbeat = HeartBeat(device_id="Patrick", timestamp=datetime.now(tz=timezone.utc))
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        frame = dash.generateViewFrame().to_dict(orient='records')

        data = [{'device_id': 'Patrick', 'uptime': 100}]
        expected = pd.DataFrame(data).to_dict(orient='records')
        assert_that(frame).is_equal_to(expected)

    def test_dashboard_view_generation(self):
        dash = DashBoard(heartbeat_interval=10, uptime_window=40)
        
        # Add heartbeats for two different devices
        now = datetime.now(tz=timezone.utc)
        dash.addHeartBeat(HeartBeat("Device1", now))
        dash.addHeartBeat(HeartBeat("Device1", now + timedelta(seconds=10)))
        dash.addHeartBeat(HeartBeat("Device2", now))
        
        frame = dash.generateViewFrame().to_dict(orient='records')
        
        # Both devices should appear in the frame
        assert_that(len(frame)).is_equal_to(2)
        devices = {row['device_id'] for row in frame}
        assert_that(devices).contains('Device1', 'Device2')


if __name__ == '__main__':
    unittest.main()
