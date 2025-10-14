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
      // update sound chart with analog percent if available
      if (typeof data.sound.percent === 'number') {
        pushSoundValue(data.sound.percent);
      } else {
        pushSoundValue(null);
      }
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

// -------------------------
// Sound intensity chart
// -------------------------
let soundChart = null;
const SOUND_BUFFER_SIZE = 60; // number of points to keep (e.g., last 2 minutes at 2s interval)
const soundBuffer = Array(SOUND_BUFFER_SIZE).fill(null);


function pushSoundValue(percent) {
  // shift buffer left and push new value
  soundBuffer.shift();
  soundBuffer.push(typeof percent === 'number' ? percent : null);
  if (soundChart) {
    soundChart.data.datasets[0].data = soundBuffer.slice();
    soundChart.update('none');
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

// -------------------------
// Raindrop history chart
// -------------------------
let raindropChart = null;

async function fetchRaindrops(n = 10) {
  const res = await fetch(`/api/raindrops?n=${n}`);
  if (!res.ok) throw new Error("Failed to fetch raindrops");
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "API returned failure");
  return json.rows || [];
}

function formatTimeLabel(isoTs) {
  // isoTs expected like "YYYY-MM-DDTHH:MM:SSZ"
  const d = new Date(isoTs);
  if (isNaN(d)) return isoTs;
  // show hours:minutes:seconds for clarity
  return d.toLocaleTimeString();
}

function buildRaindropChart(labels, values) {
  const ctx = document.getElementById('raindropChart').getContext('2d');

  if (raindropChart) {
    raindropChart.data.labels = labels;
    raindropChart.data.datasets[0].data = values;
    raindropChart.update();
    return;
  }

  raindropChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Raindrop value',
        data: values,
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.12)',
        fill: true,
        tension: 0.25,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          display: true,
          title: { display: true, text: 'Time' },
          ticks: {
            maxRotation: 45,
            autoSkip: true,
            maxTicksLimit: 10
          }
        },
        y: {
          display: true,
          beginAtZero: true,
          title: { display: true, text: 'Intensity (1 = rain, 0 = no rain)' },
          ticks: {
            // for binary rain values this keeps the scale readable
            stepSize: 1
          }
        }
      }
    }
  });
}

async function refreshRaindropChart() {
  try {
    const rows = await fetchRaindrops(10);
    const labels = rows.map(r => formatTimeLabel(r.ts));
    const values = rows.map(r => Number(r.value));
    buildRaindropChart(labels, values);
  } catch (err) {
    console.error("Could not update raindrop chart:", err);
  }
}

// -------------------------
// Sound history chart
// -------------------------
let soundHistoryChart = null;

async function fetchSounds(n = 10) {
  const res = await fetch(`/api/sounds?n=${n}`);
  if (!res.ok) throw new Error("Failed to fetch sounds");
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "API returned failure");
  return json.rows || [];
}

function buildSoundHistoryChart(labels, values) {
  const ctx = document.getElementById('soundHistoryChart').getContext('2d');

  if (soundHistoryChart) {
    soundHistoryChart.data.labels = labels;
    soundHistoryChart.data.datasets[0].data = values;
    soundHistoryChart.update();
    return;
  }

  soundHistoryChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Sound intensity (%)',
        data: values,
        borderColor: 'rgba(231, 76, 60, 1)',
        backgroundColor: 'rgba(231, 76, 60, 0.12)',
        fill: true,
        tension: 0.25,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          display: true,
          title: { display: true, text: 'Time' },
          ticks: {
            maxRotation: 45,
            autoSkip: true,
            maxTicksLimit: 10
          }
        },
        y: {
          display: true,
          beginAtZero: true,
          suggestedMax: 100,
          title: { display: true, text: 'Sound intensity (%)' }
        }
      }
    }
  });
}

async function refreshSoundHistoryChart() {
  try {
    const rows = await fetchSounds(10);
    const labels = rows.map(r => formatTimeLabel(r.ts));
    const values = rows.map(r => Number(r.value));
    buildSoundHistoryChart(labels, values);
  } catch (err) {
    console.error("Could not update sound history chart:", err);
  }
}

// initial load
document.addEventListener('DOMContentLoaded', () => {
  refreshRaindropChart();
  refreshSoundHistoryChart();
  // initialize sound chart
  // refresh every 5 seconds
  setInterval(refreshRaindropChart, 5000);
  setInterval(refreshSoundHistoryChart, 5000);
});