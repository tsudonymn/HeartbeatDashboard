from datetime import datetime, timedelta, timezone

import pandas as pd

from DeviceDashboardViewRow import DeviceDashboardViewRow


class DashBoard:
    def __init__(self, heartbeat_interval = 10, uptime_window = 3600):
        self.heartbeats = []
        self.heartbeat_interval = heartbeat_interval
        self.uptime_window = uptime_window

    def addHeartBeat(self, heartbeat):
        self.heartbeats.append(heartbeat)

    def calculateUptime(self, device_id, now = None):
        if now is None:
            now = datetime.now(tz=timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
            
        window_start = now - timedelta(seconds=self.uptime_window)
        heartbeats_for_device = self.get_heartbeats_in_window(device_id, window_start, now)
        
        # Calculate expected heartbeats based on whether 'now' aligns with interval
        expected_heartbeats = (self.uptime_window // self.heartbeat_interval)
        
        # If 'now' aligns with interval and we have heartbeats, expect one more
        if now.timestamp() % self.heartbeat_interval == 0 and heartbeats_for_device:
            expected_heartbeats += 1
            
        if not heartbeats_for_device:
            return 0
            
        calculated_uptime = len(heartbeats_for_device) / expected_heartbeats
        return int(calculated_uptime * 100)

    def generate_view_row(self, device_id):
       return DeviceDashboardViewRow(device_id=device_id, uptime=self.calculateUptime(device_id))

    def generateViewFrame(self):
        unique_ids = {hb.device_id for hb in self.heartbeats}

        view_rows = list(map(self.generate_view_row, unique_ids))

        return pd.DataFrame(view_rows)

    def heartbeats_for_device(self, device_id):
        return [hb for hb in self.heartbeats if (hb.device_id == device_id)]

    def get_heartbeats_in_window(self, device_id, window_start, window_end):
        """Get heartbeats for a device that fall within the specified time window."""
        device_heartbeats = self.heartbeats_for_device(device_id)
        # If window_end aligns with interval, include that exact time
        aligned_with_interval = window_end.timestamp() % self.heartbeat_interval == 0
        
        if aligned_with_interval:
            return [hb for hb in device_heartbeats 
                   if window_start <= hb.timestamp <= window_end]
        else:
            return [hb for hb in device_heartbeats 
                   if window_start <= hb.timestamp < window_end]

    def is_in_window(self, timestamp, window_start, window_end):
        return window_start <= timestamp <= window_end

    def calculate_expected_number_of_heartbeats(self, interval, window):
        """Calculate the number of heartbeats we expect in the window.
        If 'now' aligns with a heartbeat interval, we expect one more heartbeat.
        If 'now' falls between intervals, we expect one less heartbeat."""
        # Get the number of complete intervals
        complete_intervals = window // interval
        # Add 1 if window size is exactly divisible by interval (aligned case)
        if window % interval == 0:
            complete_intervals += 1
        return complete_intervals
