from flask import Flask, render_template, jsonify
from dht import read_dht
from raindrop import read_raindrop
from soundsensor import read_sound
from buzzer import check_alert_conditions, cleanup as buzzer_cleanup
import RPi.GPIO as GPIO
import atexit

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

def cleanup_gpio():
    """Cleanup GPIO on application shutdown"""
    buzzer_cleanup()
    GPIO.cleanup()
    print("\nGPIO cleanup completed.")

# Register cleanup function
atexit.register(cleanup_gpio)

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/sensors')
def api_sensors():
    """API endpoint to get all sensor data as JSON"""
    try:
        dht_data = read_dht()
        rain_data = read_raindrop()
        sound_data = read_sound()
        
        # Check alert conditions (both rain and sound detected)
        alert_data = check_alert_conditions(
            rain_data.get("rain_detected", False),
            sound_data.get("sound_detected", False)
        )
        
        return jsonify({
            "success": True,
            "dht": dht_data,
            "rain": rain_data,
            "sound": sound_data,
            "alert": alert_data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/dht')
def api_dht():
    """API endpoint for DHT sensor only"""
    try:
        data = read_dht()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rain')
def api_rain():
    """API endpoint for rain sensor only"""
    try:
        data = read_raindrop()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sound')
def api_sound():
    """API endpoint for sound sensor only"""
    try:
        data = read_sound()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
    finally:
        cleanup_gpio()