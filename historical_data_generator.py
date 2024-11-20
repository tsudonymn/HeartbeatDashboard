from datetime import datetime, timedelta, timezone
import random
from Heartbeat import HeartBeat
from typing import List, Dict

# Device configurations
DEVICES = [
    # Healthy devices (100% uptime)
    {"id": "device_001", "status": "healthy", "reliability": 1.0},
    {"id": "device_002", "status": "healthy", "reliability": 1.0},
    {"id": "device_003", "status": "healthy", "reliability": 1.0},
    {"id": "device_004", "status": "healthy", "reliability": 1.0},
    {"id": "device_005", "status": "healthy", "reliability": 1.0},
    {"id": "device_006", "status": "healthy", "reliability": 1.0},
    {"id": "device_007", "status": "healthy", "reliability": 1.0},
    {"id": "device_008", "status": "healthy", "reliability": 1.0},
    # Intermittent device (85% uptime)
    {"id": "device_009", "status": "intermittent", "reliability": 0.85},
    # Problematic device (60% uptime)
    {"id": "device_010", "status": "problematic", "reliability": 0.60},
    # Failed device (starts healthy, fails completely after 2 weeks)
    {"id": "device_011", "status": "fails_midway", "reliability": 1.0},
    # New device (appears only in the last week)
    {"id": "device_012", "status": "new", "reliability": 1.0}
]

class HistoricalDataGenerator:
    def __init__(self, days: int = 7, heartbeat_interval: int = 10):
        """
        Initialize the historical data generator.
        
        Args:
            days: Number of days of historical data to generate
            heartbeat_interval: Interval between heartbeats in seconds
        """
        self.days = days
        self.heartbeat_interval = heartbeat_interval
        self.end_time = datetime.now(tz=timezone.utc)
        self.start_time = self.end_time - timedelta(days=self.days)
        self.failure_date = self.start_time + timedelta(days=14)  # For device_011
        self.new_device_date = self.end_time - timedelta(days=7)  # For device_012
        
    def generate_heartbeats(self) -> List[Dict]:
        """
        Generate historical heartbeat data.
        
        Returns:
            List of dictionaries containing device_id and timestamp for each heartbeat
        """
        heartbeats = []
        current_time = self.start_time
        interval = timedelta(seconds=self.heartbeat_interval)
        
        while current_time <= self.end_time:
            for device in DEVICES:
                # Skip new device before its start date
                if device["status"] == "new" and current_time < self.new_device_date:
                    continue
                    
                # Handle device that fails midway
                if device["status"] == "fails_midway":
                    if current_time >= self.failure_date:
                        continue
                        
                # Determine if heartbeat should be sent based on reliability
                if random.random() <= device["reliability"]:
                    heartbeat = HeartBeat(
                        device_id=device["id"],
                        timestamp=current_time
                    )
                    
                    heartbeat_data = {
                        "device_id": heartbeat.device_id,
                        "timestamp": int(heartbeat.timestamp.timestamp())
                    }
                    
                    heartbeats.append(heartbeat_data)
            
            current_time += interval
        
        return heartbeats

def generate_month_of_data() -> List[Dict]:
    """
    Convenience function to generate one month of test data.
    
    Returns:
        List of heartbeat data dictionaries
    """
    generator = HistoricalDataGenerator()
    return generator.generate_heartbeats()

if __name__ == "__main__":
    # Example usage
    heartbeats = generate_month_of_data()
    print(f"Generated {len(heartbeats)} heartbeats")
    print("Sample heartbeat:", heartbeats[0] if heartbeats else "No heartbeats generated")
