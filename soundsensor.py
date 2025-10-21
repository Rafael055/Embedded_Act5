import time
import RPi.GPIO as GPIO
from smbus2 import SMBus

# GPIO Physical Pin 31 = BCM GPIO 6
# Use a clear name for the digital output (DO) pin from KY-037
SOUND_DO_PIN = 6  # BCM numbering
SOUND_DO_ACTIVE_LOW = True        # set True if module drives DO low when sound detected
ANALOG_DETECT_THRESHOLD = 15.0 

# PCF8591 I2C settings
PCF8591_I2C_ADDR = 0x48  # change if A0-A2 are set differently
PCF8591_I2C_BUS = 1
PCF8591_CHANNEL = 0  # use AIN0 (connect KY-037 AO here)


# ADC reference voltage (PCF8591 powered from 3.3V)
VREF = 3.3

# smoothing / sampling
DEFAULT_SAMPLES = 6
SAMPLE_DELAY = 0.008  # seconds between raw reads

# Calibration: baseline (silence) value to subtract from raw readings
# This allows readings to go down to 0% when silent
SILENCE_BASELINE = 128  # Adjust this based on your sensor's idle reading

_bus = None


def setup_sound_sensor():
    """Initialize DO GPIO and I2C bus for PCF8591."""
    global _bus
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    # Use internal pull-up so the DO pin has a defined idle state.
    # Many KY-037 modules drive DO LOW when sound is detected (active-low).
    # The pull-up prevents floating reads when module is disconnected or noisy.
    try:
        GPIO.setup(SOUND_DO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    except TypeError:
        # Some RPi.GPIO versions/platforms use a different signature; fallback:
        GPIO.setup(SOUND_DO_PIN, GPIO.IN)
    if _bus is None:
        _bus = SMBus(PCF8591_I2C_BUS)

def read_pcf8591_channel(channel=0, samples=DEFAULT_SAMPLES, delay=SAMPLE_DELAY):
    """
    Read a PCF8591 analog channel, returning the averaged raw 0..255 value.
    PCF8591 requires a dummy read: write control byte then discard first read.
    """
    global _bus

    # Try the I2C read with one retry. Some I2C errors (Errno 5) are transient
    # and can be resolved by reopening the bus once.
    attempts = 2
    control = 0x40 | (channel & 0x03)  # enable analog input, select channel

    for attempt in range(1, attempts + 1):
        if _bus is None:
            try:
                _bus = SMBus(PCF8591_I2C_BUS)
            except Exception as e:
                print(f"PCF8591: failed to open I2C bus {PCF8591_I2C_BUS}: {e}")
                # if we can't open the bus, no point in retrying complex read
                return None

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
            if not vals:
                return None
            return sum(vals) / len(vals)
        except Exception as e:
            # Log full exception and attempt one reopen/retry
            print(f"PCF8591 read error on attempt {attempt}: {repr(e)}")
            try:
                # try to recover by closing and reopening the bus once
                if _bus is not None:
                    try:
                        _bus.close()
                    except Exception:
                        pass
                    _bus = None
                # small pause before reopening
                time.sleep(0.05)
                if attempt == attempts:
                    # final failure
                    return None
                # otherwise loop will try to reopen and read again
            except Exception:
                return None

def read_sound(samples=DEFAULT_SAMPLES):
    """
    Read sound sensor and return both digital DO and analog AO information.
    ...
    """
    try:
        setup_sound_sensor()
        # digital DO reading (boolean)
        raw_digital = GPIO.input(SOUND_DO_PIN)
        if SOUND_DO_ACTIVE_LOW:
            sound_digital = (raw_digital == GPIO.LOW)
        else:
            sound_digital = (raw_digital == GPIO.HIGH)

        # analog reading via PCF8591
        raw = read_pcf8591_channel(PCF8591_CHANNEL, samples=samples)
        if raw is None:
            voltage = None
            percent = None
        else:
            # PCF8591 output is 0..255
            voltage = (raw / 255.0) * VREF
            # Subtract baseline for calibrated reading (0 = silence, 255 = max noise)
            calibrated_raw = max(0, raw - SILENCE_BASELINE)
            percent = (calibrated_raw / (255.0 - SILENCE_BASELINE)) * 100.0
            percent = min(100.0, max(0, percent))  # Clamp to 0-100%

        # combine signals: prefer digital, but use analog if digital is ambiguous
        detected = sound_digital
        detected_by = "digital" if sound_digital else "none"
        if not detected and percent is not None and percent >= ANALOG_DETECT_THRESHOLD:
            detected = True
            detected_by = "analog"

        # Show only percentage value as status
        if percent is not None:
            status = f"{percent:.0f}%"
        else:
            status = "No data"

        return {
            "sound_detected": detected,
            "detected_by": detected_by,
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
            # Also read raw digital numeric state for clarity
            raw_digital = GPIO.input(SOUND_DO_PIN)
            print(
                f"DO raw: {raw_digital}  | digital_detected: {data['sound_detected']} "
                f"(by={data.get('detected_by')}) | Raw(AO avg): {data['raw']} "
                f"| Volts: {data['voltage']}V | Intensity: {data['percent']}%  | {data['status']}"
            )
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cleanup()