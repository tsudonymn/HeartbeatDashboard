from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from time import gmtime, mktime


@dataclass
class HeartBeat:
    device_id: str
    timestamp: datetime

    def __init__(self, device_id=None, timestamp=None):
        if device_id is None:
            self.device_id = f"device_{gmtime()}"
        else:
            self.device_id = device_id
        
        if timestamp is None:
            self.timestamp = datetime.now(tz=timezone.utc)
        else:
            self.timestamp = timestamp if isinstance(timestamp, datetime) else datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def next(self):
        new_time = self.timestamp + timedelta(seconds=10)
        return HeartBeat(device_id=self.device_id, timestamp=new_time)
