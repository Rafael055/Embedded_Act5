import RPi.GPIO as GPIO
import dht11
import time

# DHT11 sensor on GPIO 37 = BCM 26
DHT_PIN = 26

# Initialize GPIO
GPIO.setwarnings(False)

# Cache for last valid reading
last_valid_reading = {
    "temperature": None,
    "humidity": None,
    "error": "Waiting for first reading...",
    "attempts": 0
}

def setup_dht():
    """Initialize DHT sensor GPIO"""
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)

# Create DHT11 instance
setup_dht()
instance = dht11.DHT11(pin=DHT_PIN)

def read_dht(retries=5, delay=0.5):
    global last_valid_reading
    
    for attempt in range(retries):
        result = instance.read()
        
        if result.is_valid():
            # Update cache with new valid reading
            last_valid_reading = {
                "temperature": result.temperature,
                "humidity": result.humidity,
                "error": None,
                "attempts": attempt + 1
            }
            return last_valid_reading.copy()
        
        # Wait before retry (DHT11 needs ~2 seconds between reads)
        if attempt < retries - 1:
            time.sleep(delay)
    
    # All retries failed - return last valid reading if available
    if last_valid_reading["temperature"] is not None:
        return {
            "temperature": last_valid_reading["temperature"],
            "humidity": last_valid_reading["humidity"],
            "error": "Using cached data (sensor read failed)",
            "attempts": retries,
            "cached": True
        }
    else:
        # No previous valid reading exists
        return {
            "temperature": None,
            "humidity": None,
            "error": "No data available yet",
            "attempts": retries,
            "cached": False
        }

def read_dht_console():
    """Console version with print statements"""
    data = read_dht()
    
    if data.get("cached"):
        print(f"⚠️  Using cached data (current read failed)")
        print(f"🌡️  Temperature: {data['temperature']}°C (cached)")
        print(f"💧 Humidity: {data['humidity']}% (cached)")
    elif data["error"] is None:
        temperature = data["temperature"]
        humidity = data["humidity"]
        print(f"🌡️  Temperature: {temperature}°C")
        print(f"💧 Humidity: {humidity}%")
        print(f"✅ Read on attempt: {data['attempts']}")
        return temperature, humidity
    else:
        print(f"⚠️  {data['error']}")
        print(f"❌ Failed after {data['attempts']} attempts")
        return None, None

if __name__ == "__main__":
    print("=== DHT11 Sensor Test ===")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            read_dht_console()
            print("-" * 30)
            time.sleep(3)  # DHT11 needs at least 2 seconds between reads
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()