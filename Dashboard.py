from datetime import datetime

import pandas as pd

from DeviceDashboardViewRow import DeviceDashboardViewRow


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
