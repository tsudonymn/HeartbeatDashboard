import json
from datetime import datetime
import paho.mqtt.client as mqtt
from Heartbeat import HeartBeat

class MQTTHeartbeatClient:
    def __init__(self, dashboard, broker="localhost", port=1883, topic="device/heartbeat/#"):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.broker = broker
        self.port = port
        self.topic = topic
        self.dashboard = dashboard

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to the heartbeat topic
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        try:
            # Parse the JSON message
            payload = json.loads(msg.payload.decode())
            
            # Extract device_id and timestamp
            device_id = payload.get('device_id')
            timestamp = payload.get('timestamp')
            
            if device_id and timestamp:
                # Create a new HeartBeat instance
                heartbeat = HeartBeat(device_id=device_id, timestamp=timestamp)
                # Add it to the dashboard
                self.dashboard.addHeartBeat(heartbeat)
                print(f"Added heartbeat for device {device_id}")
        except json.JSONDecodeError:
            print(f"Error decoding message: {msg.payload}")
        except Exception as e:
            print(f"Error processing message: {e}")

    def start(self):
        """Start the MQTT client"""
        try:
            self.client.connect(self.broker, self.port, 60)
            # Start the client loop in a non-blocking way
            self.client.loop_start()
            print(f"Connected to MQTT broker at {self.broker}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")

    def stop(self):
        """Stop the MQTT client"""
        self.client.loop_stop()
        self.client.disconnect()

    def publish_test_message(self):
        """Publish a test message to verify the connection"""
        test_message = {
            "device_id": "test_device",
            "timestamp": datetime.now().timestamp()
        }
        self.client.publish(self.topic.replace("#", "test"), json.dumps(test_message))
