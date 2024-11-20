import paho.mqtt.client as mqtt
import time
import json
from historical_data_generator import generate_month_of_data

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "device/heartbeat"

def connect_mqtt():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

def publish_historical_data(delay: float = 0.001):
    """
    Publish historical heartbeat data to MQTT broker.
    
    Args:
        delay: Delay between messages in seconds to avoid overwhelming the broker
    """
    print("Generating historical heartbeat data...")
    heartbeats = generate_month_of_data()
    print(f"Generated {len(heartbeats)} heartbeats")
    
    print("\nPublishing data to MQTT broker...")
    client = connect_mqtt()
    client.loop_start()
    
    for heartbeat in heartbeats:
        client.publish(MQTT_TOPIC, json.dumps(heartbeat), retain=False)
        time.sleep(delay)
    
    client.loop_stop()
    client.disconnect()
    print("Historical data publishing complete!")

if __name__ == "__main__":
    print("This script will generate and publish a month of test data with the following cases:")
    print("- 8 devices with 100% uptime")
    print("- 1 device with 85% uptime (intermittent issues)")
    print("- 1 device with 60% uptime (problematic)")
    print("- 1 device that fails completely after 2 weeks")
    print("- 1 device that only appears in the last week")
    print("\nStarting data generation and publishing...")
    
    publish_historical_data()
