class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.heartbeats = []

    def add_heartbeat(self, heartbeat):
        if heartbeat.device_id != self.device_id:
            raise ValueError(f"Heartbeat device_id {heartbeat.device_id} does not match device {self.device_id}")
        self.heartbeats.append(heartbeat)

    def get_heartbeats(self):
        return self.heartbeats.copy()  # Return a copy to prevent external modification
