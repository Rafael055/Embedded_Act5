import RPi.GPIO as GPIO
import time

# GPIO Physical Pin 35 = BCM GPIO 19
BUZZER_PIN = 19

# Initialize buzzer state
buzzer_active = False

def setup_buzzer():
    """Initialize buzzer GPIO"""
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def activate_buzzer():
    """Turn on the buzzer"""
    global buzzer_active
    setup_buzzer()
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    buzzer_active = True

def deactivate_buzzer():
    """Turn off the buzzer"""
    global buzzer_active
    setup_buzzer()
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    buzzer_active = False

def check_alert_conditions(rain_detected, sound_detected):
    """
    Check if both rain and sound are detected
    Activate/deactivate buzzer accordingly
    
    Returns:
        Dictionary with alert status
    """
    alert_active = rain_detected and sound_detected
    
    if alert_active:
        activate_buzzer()
    else:
        deactivate_buzzer()
    
    return {
        "alert_active": alert_active,
        "buzzer_on": buzzer_active,
        "message": "⚠️ ALERT: Rain and Sound Detected!" if alert_active else "System Normal"
    }

def cleanup():
    """Clean up GPIO resources"""
    deactivate_buzzer()

if __name__ == "__main__":
    print("=== Buzzer Test ===")
    print("Testing buzzer for 2 seconds...")
    
    try:
        setup_buzzer()
        print("Buzzer ON")
        activate_buzzer()
        time.sleep(2)
        print("Buzzer OFF")
        deactivate_buzzer()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cleanup()
        GPIO.cleanup()