import unittest
from dataclasses import dataclass, field
from datetime import datetime, timezone, time, timedelta
from time import gmtime, mktime

import pandas as pd
from assertpy import assert_that

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


@dataclass
class DeviceDashboardViewRow:
    device_id: str
    uptime: int = field(default_factory=lambda: datetime.fromtimestamp(0, tz=timezone.utc))


class DashBoard:
    def __init__(self, heartbeat_interval = 10, uptime_window = 3600):
        self.heartbeats = []
        self.heartbeat_interval = heartbeat_interval
        self.uptime_window = uptime_window
    def addHeartBeat(self, heartbeat):
        self.heartbeats.append(heartbeat)

    def calculateUptime(self, device_id, now = datetime.now()):
        expected_number_of_heartbeats = self.calculate_expected_number_of_heartbeats(self.heartbeat_interval, self.uptime_window)
        heartbeats_for_device = self.heartbeats_for_device(device_id)
        calculated_uptime = len(heartbeats_for_device) / expected_number_of_heartbeats

        return int(calculated_uptime * 100)

    def generate_view_row(self, device_id):
       return DeviceDashboardViewRow(device_id=device_id, uptime=self.calculateUptime(device_id))

    def generateViewFrame(self):
        unique_ids = {hb.device_id for hb in self.heartbeats}

        view_rows = list(map(self.generate_view_row, unique_ids))

        return pd.DataFrame(view_rows)

    def heartbeats_for_device(self, device_id):
        return [hb for hb in self.heartbeats if (hb.device_id == device_id)]

    def calculate_expected_number_of_heartbeats(self, interval, window):
        return self.uptime_window / self.heartbeat_interval


class HeartBeat:
    def __init__(self, device_id=None, timestamp=None):
        if device_id is None:
            self.device_id: str = field(default_factory=lambda:f"device_{gmtime()}" )
        else:
            self.device_id = device_id
            self.timestamp: datetime = field(default_factory=lambda: datetime.fromtimestamp(timestamp, tz=timezone.utc))

    def next(self):
        current_gmt = gmtime()

        current_gmt_datetime = datetime.fromtimestamp(mktime(current_gmt), tz=timezone.utc)

        new_time = current_gmt_datetime + timedelta(seconds=10)
        return HeartBeat(device_id=self.device_id, timestamp=new_time)


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
        heartbeat = HeartBeat(device_id = "Patrick", timestamp = datetime.now(tz=timezone.utc))
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


if __name__ == '__main__':
    unittest.main()
