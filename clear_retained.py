import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "device/heartbeat"  # Base topic without wildcards

def clear_retained_messages():
    print("Clearing retained messages...")
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Publish an empty message with retain=True to clear any retained messages
    client.publish(MQTT_TOPIC, "", retain=True)
    
    client.disconnect()
    print("Retained messages cleared!")

if __name__ == "__main__":
    clear_retained_messages()
