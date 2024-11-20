import paho.mqtt.client as mqtt
import time
from datetime import datetime, timedelta, timezone
import random
import json
from Heartbeat import HeartBeat

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "device/heartbeat"

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

def connect_mqtt():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

def generate_historical_data():
    client = connect_mqtt()
    client.loop_start()
    
    # Calculate time ranges
    end_time = datetime.now(tz=timezone.utc)
    start_time = end_time - timedelta(days=30)
    current_time = start_time
    
    # Interval between heartbeats (10 seconds)
    heartbeat_interval = timedelta(seconds=10)
    
    # For device_011 (fails midway)
    failure_date = start_time + timedelta(days=14)
    
    # For device_012 (new device)
    new_device_date = end_time - timedelta(days=7)
    
    while current_time <= end_time:
        for device in DEVICES:
            # Skip new device before its start date
            if device["status"] == "new" and current_time < new_device_date:
                continue
                
            # Handle device that fails midway
            if device["status"] == "fails_midway":
                if current_time >= failure_date:
                    continue
                    
            # Determine if heartbeat should be sent based on reliability
            if random.random() <= device["reliability"]:
                heartbeat = HeartBeat(
                    device_id=device["id"],
                    timestamp=current_time
                )
                
                # Convert timestamp to int for MQTT transmission
                heartbeat_data = {
                    "device_id": heartbeat.device_id,
                    "timestamp": int(heartbeat.timestamp.timestamp())
                }
                
                # Publish heartbeat
                client.publish(MQTT_TOPIC, json.dumps(heartbeat_data), retain=False)
                
        # Move to next interval
        current_time += heartbeat_interval
        
        # Add a small delay to avoid overwhelming the broker
        time.sleep(0.001)
    
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    print("Generating historical heartbeat data...")
    print("This will generate data for the past 30 days with the following test cases:")
    print("- 8 devices with 100% uptime")
    print("- 1 device with 85% uptime (intermittent issues)")
    print("- 1 device with 60% uptime (problematic)")
    print("- 1 device that fails completely after 2 weeks")
    print("- 1 device that only appears in the last week")
    print("\nStarting data generation...")
    
    generate_historical_data()
    
    print("Historical data generation complete!")
