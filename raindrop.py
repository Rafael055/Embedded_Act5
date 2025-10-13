import RPi.GPIO as GPIO
import time
import time

# GPIO pin configuration
RAIN_PIN = 13  # Change this to your actual rain sensor digital pin

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RAIN_PIN, GPIO.IN)
from database import insert_raindrop

def read_raindrop():
    value = None
    try:
        # Read digital pin (LOW = rain detected, HIGH = no rain)
        rain_detected = GPIO.input(RAIN_PIN) == GPIO.LOW

        # numeric value for history: 1.0 = rain, 0.0 = no rain
        numeric = 1.0 if rain_detected else 0.0
        try:
            insert_raindrop(numeric)
        except Exception as e:
            # don't break sensor reading loop for DB errors
            print(f"Warning: failed to insert raindrop into DB: {e}")

        return {
            "rain_detected": rain_detected,
            "value": numeric,
            "status": "🌧️ Rain detected" if rain_detected else "☀️ Sunny"
        }
    except Exception as e:
        print(f"Error reading raindrop sensor: {e}")
        return {
            "rain_detected": None,
            "status": f"Error: {str(e)}"
        }

def cleanup():
    """Clean up GPIO resources"""
    GPIO.cleanup()

if __name__ == "__main__":
    print("Testing Raindrop Sensor (Press Ctrl+C to exit)")
    try:
        while True:
            data = read_raindrop()
            print(f"Rain Status: {data['status']}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cleanup()