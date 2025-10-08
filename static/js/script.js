// Fetch sensor data from API
async function fetchSensorData() {
  try {
    const response = await fetch('/api/sensors');
    const data = await response.json();

    if (data.success) {
      updateDHTDisplay(data.dht);
      updateRainDisplay(data.rain);
      updateSoundDisplay(data.sound);
      updateAlertDisplay(data.alert);
    } else {
      console.error('Error fetching sensor data:', data.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Update DHT sensor display
function updateDHTDisplay(dht) {
  const tempElement = document.getElementById('temperature');
  const humidityElement = document.getElementById('humidity');

  if (dht.temperature !== null && dht.humidity !== null) {
    tempElement.textContent = `${dht.temperature}°C`;
    humidityElement.textContent = `${dht.humidity}%`;

    if (dht.cached) {
      tempElement.style.opacity = '0.7';
      humidityElement.style.opacity = '0.7';
    } else {
      tempElement.style.opacity = '1';
      humidityElement.style.opacity = '1';
    }
  } else {
    tempElement.textContent = 'Loading...';
    humidityElement.textContent = 'Loading...';
  }
}

// Update rain sensor display
function updateRainDisplay(rain) {
  const statusElement = document.getElementById('rain-status');

  if (rain.rain_detected !== null) {
    statusElement.textContent = rain.status;

    if (rain.rain_detected) {
      statusElement.style.color = '#3498db';
      statusElement.style.fontWeight = 'bold';
    } else {
      statusElement.style.color = '#2ecc71';
      statusElement.style.fontWeight = 'normal';
    }
  } else {
    statusElement.textContent = 'Loading...';
  }
}

// Update sound sensor display
function updateSoundDisplay(sound) {
  const statusElement = document.getElementById('sound-status');

  if (sound.sound_detected !== null) {
    statusElement.textContent = sound.status;

    if (sound.sound_detected) {
      statusElement.style.color = '#e74c3c';
      statusElement.style.fontWeight = 'bold';
    } else {
      statusElement.style.color = '#95a5a6';
      statusElement.style.fontWeight = 'normal';
    }
  } else {
    statusElement.textContent = 'Loading...';
  }
}

// Update alert display (buzzer and warning)
function updateAlertDisplay(alert) {
  const warningOverlay = document.getElementById('warning-overlay');
  const alertStatus = document.getElementById('alert-status');
  const alertMessage = document.getElementById('alert-message');

  if (alert.alert_active) {
    // Show warning overlay with flashing animation
    warningOverlay.classList.remove('hidden');

    // Update alert status
    alertStatus.classList.remove('hidden');
    alertStatus.classList.add('active');
    alertMessage.textContent = alert.message;
  } else {
    // Hide warning overlay
    warningOverlay.classList.add('hidden');

    // Update alert status to normal
    alertStatus.classList.remove('active');
    alertMessage.textContent = alert.message;
  }
}

// Auto-refresh every 2 seconds
setInterval(fetchSensorData, 2000);

// Initial fetch when page loads
document.addEventListener('DOMContentLoaded', fetchSensorData);