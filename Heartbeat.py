from dataclasses import field
from datetime import datetime, timezone, timedelta
from time import gmtime, mktime


class HeartBeat:
    def __init__(self, device_id=None, timestamp=None):
        if device_id is None:
            self.device_id = f"device_{gmtime()}"
        else:
            self.device_id = device_id
        
        self.timestamp = timestamp if timestamp else datetime.now(tz=timezone.utc)

    def next(self):
        new_time = self.timestamp + timedelta(seconds=10)
        return HeartBeat(device_id=self.device_id, timestamp=new_time)
