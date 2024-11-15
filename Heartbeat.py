from dataclasses import field
from datetime import datetime, timezone, timedelta
from time import gmtime, mktime


class HeartBeat:
    def __init__(self, device_id=None, timestamp=None):
        if device_id is None:
            self.device_id: str = field(default_factory=lambda:f"device_{gmtime()}" )
        else:
            self.device_id = device_id
            self.timestamp: datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def next(self):
        current_gmt = gmtime()

        current_gmt_datetime = datetime.fromtimestamp(mktime(current_gmt), tz=timezone.utc)

        new_time = current_gmt_datetime + timedelta(seconds=10)
        return HeartBeat(device_id=self.device_id, timestamp=new_time)
