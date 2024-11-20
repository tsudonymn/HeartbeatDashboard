import unittest
from datetime import datetime, timezone, timedelta
from assertpy import assert_that

from Device import Device
from Heartbeat import HeartBeat


class DeviceTest(unittest.TestCase):
    def test_calc_uptime(self):
        device = Device("Patrick")
        interval = 10
        window = 30
        now = datetime.now(tz=timezone.utc)
        
        # Add three heartbeats at 0s, 10s, and 20s
        heartbeat = HeartBeat("Patrick", now)
        device.add_heartbeat(heartbeat)
        device.add_heartbeat(HeartBeat("Patrick", now + timedelta(seconds=10)))
        device.add_heartbeat(HeartBeat("Patrick", now + timedelta(seconds=20)))

        uptime = device.calculate_uptime(interval, window, now + timedelta(seconds=20))
        assert_that(uptime).is_equal_to(100)

    def test_calc_uptime_with_missing_heartbeats(self):
        device = Device("Patrick")
        interval = 10
        window = 60
        now = datetime.now(tz=timezone.utc)

        # Add five heartbeats (missing the last one in a 60s window)
        heartbeat = HeartBeat("Patrick", now)
        device.add_heartbeat(heartbeat)
        device.add_heartbeat(HeartBeat("Patrick", now + timedelta(seconds=10)))
        device.add_heartbeat(HeartBeat("Patrick", now + timedelta(seconds=20)))
        device.add_heartbeat(HeartBeat("Patrick", now + timedelta(seconds=30)))
        device.add_heartbeat(HeartBeat("Patrick", now + timedelta(seconds=40)))

        uptime = device.calculate_uptime(interval, window, now + timedelta(seconds=60))
        assert_that(uptime).is_equal_to(83)  # 5 out of 6 expected heartbeats = 83%

    def test_calc_uptime_with_no_heartbeats(self):
        device = Device("Patrick")
        interval = 10
        window = 30
        now = datetime.now(tz=timezone.utc)

        uptime = device.calculate_uptime(interval, window, now)
        assert_that(uptime).is_equal_to(0)

    def test_add_heartbeat_validation(self):
        device = Device("Patrick")
        wrong_heartbeat = HeartBeat("WrongDevice", datetime.now(tz=timezone.utc))
        
        with self.assertRaises(ValueError) as context:
            device.add_heartbeat(wrong_heartbeat)
        
        assert_that(str(context.exception)).contains("does not match device")


if __name__ == '__main__':
    unittest.main()
