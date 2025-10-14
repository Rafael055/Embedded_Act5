import time
import RPi.GPIO as GPIO
from smbus2 import SMBus

# GPIO Physical Pin 31 = BCM GPIO 6
SOUND_PIN = 6  # BCM numbering

# PCF8591 I2C settings
PCF8591_I2C_ADDR = 0x48  # change if A0-A2 are set differently
PCF8591_I2C_BUS = 1
PCF8591_CHANNEL = 0  # use AIN0 (connect KY-037 AO here)


# ADC reference voltage (PCF8591 powered from 3.3V)
VREF = 3.3

# smoothing / sampling
DEFAULT_SAMPLES = 6
SAMPLE_DELAY = 0.008  # seconds between raw reads

_bus = None


def setup_sound_sensor():
    """Initialize DO GPIO and I2C bus for PCF8591."""
    global _bus
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    GPIO.setup(SOUND_DO_PIN, GPIO.IN)
    if _bus is None:
        _bus = SMBus(PCF8591_I2C_BUS)

def read_pcf8591_channel(channel=0, samples=DEFAULT_SAMPLES, delay=SAMPLE_DELAY):
    """
    Read a PCF8591 analog channel, returning the averaged raw 0..255 value.
    PCF8591 requires a dummy read: write control byte then discard first read.
    """
    global _bus
    if _bus is None:
        _bus = SMBus(PCF8591_I2C_BUS)
    control = 0x40 | (channel & 0x03)  # enable analog input, select channel
    vals = []
    try:
        for _ in range(samples):
            # Write control byte to select channel
            _bus.write_byte(PCF8591_I2C_ADDR, control)
            # First read is a dummy; second read returns valid data
            _bus.read_byte(PCF8591_I2C_ADDR)  # discard
            raw = _bus.read_byte(PCF8591_I2C_ADDR)
            vals.append(raw)
            time.sleep(delay)
    except Exception as e:
        # Re-raise or return None in calling function; print for debugging
        print(f"PCF8591 read error: {e}")
        return None
    if not vals:
        return None
    return sum(vals) / len(vals)

def read_sound(samples=DEFAULT_SAMPLES):
    """
    Read sound sensor and return both digital DO and analog AO information.
    Returns a dict:
      {
        "sound_detected": bool or None,   # from DO pin
        "raw": 0..255 or None,            # averaged analog raw ADC value
        "voltage": volts or None,         # scaled to VREF
        "percent": 0.0..100.0 or None,    # percent of full scale
        "status": "..."                   # human-friendly status
      }
    """
    try:
        setup_sound_sensor()
        # digital DO reading (boolean)
        sound_detected = GPIO.input(SOUND_DO_PIN) == GPIO.HIGH

        # analog reading via PCF8591
        raw = read_pcf8591_channel(PCF8591_CHANNEL, samples=samples)
        if raw is None:
            voltage = None
            percent = None
        else:
            # PCF8591 output is 0..255
            voltage = (raw / 255.0) * VREF
            percent = (raw / 255.0) * 100.0

        status = "Sound detected" if sound_detected else "Quiet"
        if percent is not None:
            status += f" — {percent:.0f}% intensity"

        return {
            "sound_detected": sound_detected,
            "raw": None if raw is None else float(raw),
            "voltage": None if voltage is None else round(voltage, 3),
            "percent": None if percent is None else round(percent, 1),
            "status": status
        }
    except Exception as e:
        print(f"Error reading sound sensor: {e}")
        return {
            "sound_detected": None,
            "raw": None,
            "voltage": None,
            "percent": None,
            "status": f"Error: {e}"
        }

def cleanup():
    """Close I2C bus and cleanup GPIO."""
    global _bus
    try:
        if _bus is not None:
            _bus.close()
            _bus = None
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass

if __name__ == "__main__":
    print("=== KY-037 + PCF8591 Sound Sensor Test ===")
    print("DO (digital) -> BCM 6 ; AO -> PCF8591 AIN0")
    print("Press Ctrl+C to exit\n")
    try:
        while True:
            data = read_sound()
            print(f"Digital: {data['sound_detected']}, Raw: {data['raw']}, "
                  f"Volts: {data['voltage']}V, Intensity: {data['percent']}%  | {data['status']}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cleanup()