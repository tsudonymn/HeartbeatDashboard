from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DeviceDashboardViewRow:
    device_id: str
    uptime: int = -1
    last_seen: float = 0.0

    def to_dict(self):
        dt = datetime.fromtimestamp(self.last_seen, tz=timezone.utc)
        return {"devic_id": self.device_id, "uptime": self.uptime, "last_seen": dt.isoformat()}
