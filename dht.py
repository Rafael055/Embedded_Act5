import RPi.GPIO as GPIO
import dht11
import time

# DHT11 sensor on GPIO 37 = BCM 26
DHT_PIN = 26

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# Create DHT11 instance
instance = dht11.DHT11(pin=DHT_PIN)

def read_dht():
    result = instance.read()
    
    if result.is_valid():
        temperature = result.temperature
        humidity = result.humidity
        print(f"🌡️  Temperature: {temperature}°C")
        print(f"💧 Humidity: {humidity}%")
        return temperature, humidity
    else:
        print("⚠️  Failed to retrieve data from DHT sensor")
        return None, None

if __name__ == "__main__":
    print("=== DHT11 Sensor Test ===")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            read_dht()
            print("-" * 30)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()