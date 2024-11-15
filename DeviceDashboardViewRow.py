from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DeviceDashboardViewRow:
    device_id: str
    uptime: int = field(default_factory=lambda: datetime.fromtimestamp(0, tz=timezone.utc))
