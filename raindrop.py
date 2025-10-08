import RPi.GPIO as GPIO
import time

# GPIO pin configuration
RAIN_PIN = 13  # Change this to your actual rain sensor digital pin

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RAIN_PIN, GPIO.IN)

def read_raindrop():
    """
    Read the raindrop sensor status
    Returns a dictionary with rain detection status
    """
    try:
        # Read digital pin (LOW = rain detected, HIGH = no rain)
        rain_detected = GPIO.input(RAIN_PIN) == GPIO.LOW
        
        return {
            "rain_detected": rain_detected,
            "status": "🌧️Rain detected" if rain_detected else "☀️Sunny"
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