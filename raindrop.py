import RPi.GPIO as GPIO
import time

# GPIO 33 = BCM 13
RAINDROP_PIN = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(RAINDROP_PIN, GPIO.IN)

def read_raindrop():
    # Digital Output (DO): LOW = Rain detected, HIGH = No rain
    rain_detected = GPIO.input(RAINDROP_PIN) == GPIO.LOW
    
    if rain_detected:
        print("💧💧 RAIN DETECTED! 💧💧")
    else:
        print("☀️  No rain detected")
    
    return rain_detected

if __name__ == "__main__":
    print("=== Raindrop Sensor Test ===")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            read_raindrop()
            print("-" * 30)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()