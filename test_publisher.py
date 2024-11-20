import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import random

class HeartbeatPublisher:
    def __init__(self, broker="localhost", port=1883):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic_base = "device/heartbeat"
        self.devices = [f"device_{i}" for i in range(1, 4)]  # Simulate 3 devices
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        
    def connect(self):
        self.client.on_connect = self.on_connect
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print(f"Connected to MQTT broker at {self.broker}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
            
    def publish_heartbeat(self, device_id):
        message = {
            "device_id": device_id,
            "timestamp": datetime.now().timestamp()
        }
        topic = f"{self.topic_base}/{device_id}"
        self.client.publish(topic, json.dumps(message), retain=False)
        print(f"Published heartbeat for {device_id}")
        
    def simulate_devices(self, duration_seconds=60, interval_seconds=10):
        """Simulate devices sending heartbeats for a specified duration"""
        print(f"Starting simulation for {duration_seconds} seconds...")
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # Randomly skip some heartbeats to simulate device issues
            for device_id in self.devices:
                if random.random() > 0.1:  # 90% chance to send heartbeat
                    self.publish_heartbeat(device_id)
            
            time.sleep(interval_seconds)
            
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("Publisher stopped")

if __name__ == "__main__":
    publisher = HeartbeatPublisher()
    if publisher.connect():
        try:
            # Run simulation for 5 minutes with heartbeats every 10 seconds
            publisher.simulate_devices(duration_seconds=300, interval_seconds=10)
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        finally:
            publisher.stop()
