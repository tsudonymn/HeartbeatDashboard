from datetime import datetime

import pandas as pd

from DeviceDashboardViewRow import DeviceDashboardViewRow
from Device import Device


class DashBoard:
    def __init__(self, heartbeat_interval = 10, uptime_window = 3600):
        self.devices = {}  # Dictionary mapping device_id to Device objects
        self.heartbeat_interval = heartbeat_interval
        self.uptime_window = uptime_window

    def addHeartBeat(self, heartbeat):
        device_id = heartbeat.device_id
        if device_id not in self.devices:
            self.devices[device_id] = Device(device_id)
        self.devices[device_id].add_heartbeat(heartbeat)

    def calculateUptime(self, device_id, now = datetime.now()):
        expected_number_of_heartbeats = self.calculate_expected_number_of_heartbeats(self.heartbeat_interval, self.uptime_window)
        heartbeats_for_device = self.heartbeats_for_device(device_id)
        if not heartbeats_for_device:
            return 0
        calculated_uptime = len(heartbeats_for_device) / expected_number_of_heartbeats
        return int(calculated_uptime * 100)

    def generate_view_row(self, device_id):
       return DeviceDashboardViewRow(device_id=device_id, uptime=self.calculateUptime(device_id))

    def generateViewFrame(self):
        unique_ids = set(self.devices.keys())
        view_rows = list(map(self.generate_view_row, unique_ids))
        return pd.DataFrame(view_rows)

    def heartbeats_for_device(self, device_id):
        device = self.devices.get(device_id)
        return device.get_heartbeats() if device else []

    def calculate_expected_number_of_heartbeats(self, interval, window):
        return self.uptime_window / self.heartbeat_interval
