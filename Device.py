from datetime import datetime


class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.heartbeats = []
        self.most_recent_heartbeat = None

    def add_heartbeat(self, heartbeat):
        if heartbeat.device_id != self.device_id:
            raise ValueError(f"Heartbeat device_id {heartbeat.device_id} does not match device {self.device_id}")
        self.heartbeats.append(heartbeat)
        if self.most_recent_heartbeat is None or heartbeat.timestamp > self.most_recent_heartbeat.timestamp:
            self.most_recent_heartbeat = heartbeat

    def get_heartbeats(self):
        return self.heartbeats.copy()  # Return a copy to prevent external modification

    def get_last_seen(self):
        return self.most_recent_heartbeat.timestamp if self.most_recent_heartbeat else datetime.fromtimestamp(0, tz=datetime.utcnow().astimezone().tzinfo)

    def calculate_uptime(self, heartbeat_interval, uptime_window, now=datetime.now()):
        expected_heartbeats = uptime_window / heartbeat_interval
        if not self.heartbeats:
            return 0
        calculated_uptime = len(self.heartbeats) / expected_heartbeats
        return int(calculated_uptime * 100)
