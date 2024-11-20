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
    def test_last_seen_defaults_to_beginning_of_time(self):
        device = DeviceDashboardViewRow(' ')
        assert_that(device.last_seen).is_equal_to(datetime.fromtimestamp(0, tz=timezone.utc))  # add assertion here

    def test_given_datetime_sets_last_seen(self):
        nownow = datetime.now(tz=timezone.utc)
        device = DeviceDashboardViewRow(' ', last_seen=nownow)
        assert_that(device.last_seen).is_equal_to(nownow)

    def test_generate_view_frame_with_perfect_uptime(self):
        dash = DashBoard(heartbeat_interval=10, uptime_window=40)
        now = datetime.now(tz=timezone.utc)
        heartbeat = HeartBeat(device_id="Patrick", timestamp=now)
        dash.addHeartBeat(heartbeat)
        dash.addHeartBeat(heartbeat.next())
        dash.addHeartBeat(heartbeat.next())
        last_heartbeat = heartbeat.next()
        dash.addHeartBeat(last_heartbeat)
        
        frame = dash.generateViewFrame()
        records = frame.to_dict(orient='records')
        
        # Verify each field separately
        assert_that(records).is_length(1)
        record = records[0]
        assert_that(record['device_id']).is_equal_to('Patrick')
        assert_that(record['uptime']).is_equal_to(100)
        assert_that(record['last_seen'].timestamp()).is_close_to(last_heartbeat.timestamp.timestamp(), tolerance=1)

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
