import RPi.GPIO as GPIO
import time

# GPIO 31 = BCM 6
SOUND_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(SOUND_PIN, GPIO.IN)

def read_sound():
    # Digital Output (DO): HIGH = Sound detected, LOW = No sound
    sound_detected = GPIO.input(SOUND_PIN) == GPIO.HIGH
    
    if sound_detected:
        print("🔊🔊 SOUND DETECTED! 🔊🔊")
    else:
        print("🔇 Quiet...")
    
    return sound_detected

if __name__ == "__main__":
    print("=== Sound Sensor Test ===")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            read_sound()
            print("-" * 30)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()