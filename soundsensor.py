import RPi.GPIO as GPIO
import time

# GPIO Physical Pin 31 = BCM GPIO 6
SOUND_PIN = 6  # BCM numbering

def setup_sound_sensor():
    """Initialize sound sensor GPIO"""
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(SOUND_PIN, GPIO.IN)

def read_sound():
    """
    Read the sound sensor status
    Returns a dictionary with sound detection status
    """
    try:
        setup_sound_sensor()
        # Digital Output (DO): HIGH = Sound detected, LOW = No sound
        sound_detected = GPIO.input(SOUND_PIN) == GPIO.HIGH
        
        return {
            "sound_detected": sound_detected,
            "status": "Sound detected" if sound_detected else "Quiet"
        }
    except Exception as e:
        print(f"Error reading sound sensor: {e}")
        return {
            "sound_detected": None,
            "status": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    print("=== Sound Sensor Test ===")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            result = read_sound()
            if result["sound_detected"]:
                print("🔊🔊 SOUND DETECTED! 🔊🔊")
            else:
                print("🔇 Quiet...")
            print(f"Status: {result['status']}")
            print("-" * 30)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()