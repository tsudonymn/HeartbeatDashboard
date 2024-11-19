from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DeviceDashboardViewRow:
    device_id: str
    uptime: int = 0
