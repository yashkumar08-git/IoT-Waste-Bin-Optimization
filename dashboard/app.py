
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

bin_data = {
    "distance_cm": None,
    "fill_percent": None,
    "dry_fill_percent": None,
    "wet_fill_percent": None,
    "latitude": None,
    "longitude": None,
    "status": "WAITING FOR SENSOR",
    "updated_at": "No readings received yet"
}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Smart Waste | Control Center</title>
<style>
:root {
  --bg: #0b1120;
  --panel: #141e31;
  --muted: #9baac2;
  --text: #f2f6ff;
  --green: #39d98a;
  --blue: #62a8ff;
  --orange: #ffbd69;
  --border: #28364c;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: radial-gradient(ellipse at top left, #182a43, var(--bg) 55%);
  color: var(--text);
  font-family: Inter, Segoe UI, Arial, sans-serif;
}
main { max-width: 1180px; margin: auto; padding: 32px 20px 50px; }
.topbar {
  display: flex; justify-content: space-between; align-items: center;
  gap: 16px; flex-wrap: wrap; margin-bottom: 30px;
}
.brand { display: flex; align-items: center; gap: 14px; }
.logo {
  width: 52px; height: 52px; border-radius: 16px;
  display: grid; place-items: center; font-size: 26px;
  background: linear-gradient(135deg, #35d995, #128b82);
  box-shadow: 0 8px 30px #20c99725;
}
.eyebrow {
  color: var(--green); font-size: 11px; font-weight: 800;
  letter-spacing: 2px; text-transform: uppercase;
}
h1 { font-size: clamp(24px, 4vw, 34px); margin: 5px 0; }
h2 { font-size: 18px; margin: 0 0 8px; }
p { color: var(--muted); line-height: 1.6; }
.top-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.pill {
  border: 1px solid var(--border); border-radius: 30px;
  padding: 10px 14px; color: var(--muted); font-size: 12px;
  background: #111b2b;
}
.dot {
  display: inline-block; width: 8px; height: 8px;
  border-radius: 50%; background: var(--green); margin-right: 7px;
}
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.card {
  min-width: 0; padding: 23px; border-radius: 22px;
  background: linear-gradient(145deg, #18243a, #111a2b);
  border: 1px solid var(--border);
  box-shadow: 0 12px 35px #00000018;
}
.wide { grid-column: span 2; }
.full { grid-column: 1 / -1; }
.card-head {
  display: flex; justify-content: space-between;
  align-items: center; gap: 10px; margin-bottom: 22px;
}
.tag {
  padding: 7px 10px; border-radius: 20px; font-size: 11px;
  font-weight: 700; background: #22334a; color: var(--muted);
}
.big { font-size: clamp(30px, 4vw, 43px); font-weight: 800; margin: 8px 0; }
.small { color: var(--muted); font-size: 13px; }
.track {
  width: 100%; height: 10px; background: #29364a;
  border-radius: 20px; overflow: hidden; margin: 18px 0 12px;
}
.bar { height: 100%; width: 0%; border-radius: 20px; transition: width .5s ease; }
.green { background: linear-gradient(90deg, #16b978, #55edaa); }
.blue { background: linear-gradient(90deg, #397be8, #72bcff); }
.orange { background: linear-gradient(90deg, #e89b34, #ffd078); }
.stat-row { display: flex; justify-content: space-between; gap: 10px; }
.stat-row span { color: var(--muted); font-size: 12px; }
.stat-row strong { font-size: 13px; }
.location-box {
  background: #0d1727; border: 1px solid var(--border);
  border-radius: 16px; padding: 18px;
}
.coords { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 18px 0; }
.coord {
  padding: 13px; background: #18253a; border-radius: 12px;
  overflow-wrap: anywhere;
}
.coord label { display: block; color: var(--muted); font-size: 11px; margin-bottom: 8px; }
.coord strong { font-size: 14px; }
button, .map-link {
  display: inline-block; border: 0; border-radius: 12px;
  padding: 12px 16px; font-weight: 700; cursor: pointer;
  text-decoration: none; font-size: 13px;
}
button { color: #071a17; background: var(--green); }
.map-link { color: #d9e9ff; background: #223957; }
button:hover, .map-link:hover { opacity: .85; }
.notice { font-size: 12px; margin-top: 14px; }
.footer { text-align: center; font-size: 12px; color: #7889a3; margin-top: 26px; }
@media(max-width: 760px) {
  .grid { grid-template-columns: 1fr; }
  .wide, .full { grid-column: auto; }
  main { padding: 22px 14px; }
}
</style>
</head>
<body>
<main>
  <header class="topbar">
    <div class="brand">
      <div class="logo">♻</div>
      <div>
        <div class="eyebrow">IoT Waste Management</div>
        <h1>Smart Waste Control Center</h1>
        <div class="small">Real-time monitoring · GPS tracking</div>
      </div>
    </div>
    <div class="top-actions">
      <div class="pill"><span class="dot"></span>Dashboard online</div>
      <div class="pill">BIN-001 · Physical unit</div>
    </div>
  </header>

  <section class="grid">
    <div class="card">
      <div class="card-head">
        <h2>♻ Overall Fill</h2>
        <span class="tag" id="overallTag">Waiting</span>
      </div>
      <div class="small">Overall bin fill level</div>
      <div class="big"><span id="overall">--</span><span>%</span></div>
      <div class="track"><div class="bar green" id="overallBar"></div></div>
      <div class="stat-row">
        <span>Collection status</span><strong id="overallStatus">Waiting for sensor</strong>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <h2>🟢 Dry Waste</h2>
        <span class="tag">Compartment A</span>
      </div>
      <div class="small">Paper, plastic and other dry waste</div>
      <div class="big"><span id="dry">--</span><span>%</span></div>
      <div class="track"><div class="bar green" id="dryBar"></div></div>
      <div class="stat-row">
        <span>Fill level</span><strong id="dryStatus">No reading</strong>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <h2>🔵 Wet Waste</h2>
        <span class="tag">Compartment B</span>
      </div>
      <div class="small">Food scraps and biodegradable waste</div>
      <div class="big"><span id="wet">--</span><span>%</span></div>
      <div class="track"><div class="bar blue" id="wetBar"></div></div>
      <div class="stat-row">
        <span>Fill level</span><strong id="wetStatus">No reading</strong>
      </div>
    </div>

    <div class="card wide">
      <div class="card-head">
        <h2>📍 GPS Location</h2>
        <span class="tag" id="gpsTag">GPS unavailable</span>
      </div>
      <div class="location-box">
        <div class="small">Registered location of physical bin</div>
        <div class="coords">
          <div class="coord">
            <label>LATITUDE</label>
            <strong id="latitude">Not available</strong>
          </div>
          <div class="coord">
            <label>LONGITUDE</label>
            <strong id="longitude">Not available</strong>
          </div>
        </div>
        <a id="mapLink" class="map-link" href="#" target="_blank"
           rel="noopener noreferrer" style="display:none">Open in Google Maps ↗</a>
        <p id="gpsMessage" class="notice">Waiting for GPS coordinates from ESP32.</p>
      </div>
    </div>

    <div class="card">
      <div class="card-head"><h2>📡 Sensor Health</h2><span class="tag">Live</span></div>
      <p class="small">Ultrasonic sensor distance</p>
      <div class="big"><span id="distance">--</span> <span style="font-size:17px">cm</span></div>
      <div class="track"><div class="bar orange" id="distanceBar"></div></div>
      <div class="stat-row"><span>Last update</span><strong id="updated">Not received</strong></div>
      <p id="connection" class="notice">Waiting for sensor data.</p>
      <button onclick="refreshData()">↻ Refresh data</button>
    </div>

    <div class="card full">
      <div class="card-head">
        <div>
          <h2>Collection Overview</h2>
          <div class="small">Live collection alerts from the latest sensor readings</div>
        </div>
        <span class="tag" id="alertCount">0 alerts</span>
      </div>
      <p id="alerts">No readings received yet. Connect the ESP32 to begin monitoring.</p>
    </div>
  </section>
  <div class="footer">SMART WASTE MANAGEMENT SYSTEM · ESP32 + ULTRASONIC + GPS</div>
</main>

<script>
function setText(id, value) {
  document.getElementById(id).textContent = value;
}
function setFill(id, value, colorClass) {
  const bar = document.getElementById(id);
  bar.style.width = value === null || value === undefined
    ? '0%' : Math.max(0, Math.min(100, value)) + '%';
  bar.className = 'bar ' + colorClass;
}
function formatFill(value) {
  return value === null || value === undefined ? '--' : Number(value).toFixed(1);
}
function fillStatus(value) {
  if (value === null || value === undefined) return 'No reading';
  if (value >= 80) return 'Collection needed';
  if (value >= 60) return 'High';
  if (value >= 30) return 'Medium';
  return 'Low';
}
async function refreshData() {
  try {
    const response = await fetch('/api/bin', {cache: 'no-store'});
    if (!response.ok) throw new Error('API unavailable');
    const d = await response.json();

    const overall = d.fill_percent;
    setText('overall', formatFill(overall));
    setFill('overallBar', overall, overall >= 80 ? 'orange' : 'green');
    setText('overallStatus', fillStatus(overall));
    setText('overallTag', overall === null ? 'Waiting' : fillStatus(overall));

    setText('dry', formatFill(d.dry_fill_percent));
    setFill('dryBar', d.dry_fill_percent, 'green');
    setText('dryStatus', fillStatus(d.dry_fill_percent));

    setText('wet', formatFill(d.wet_fill_percent));
    setFill('wetBar', d.wet_fill_percent, 'blue');
    setText('wetStatus', fillStatus(d.wet_fill_percent));

    setText('distance', d.distance_cm == null ? '--' : d.distance_cm);
    setFill('distanceBar', d.distance_cm == null ? 0 :
      Math.min(100, Number(d.distance_cm) / 4), 'orange');
    setText('updated', d.updated_at);
    setText('connection', overall == null &&
      d.dry_fill_percent == null && d.wet_fill_percent == null
      ? 'Waiting for ESP32 sensor data.' : 'Latest data received by dashboard.');

    const hasGps = d.latitude != null && d.longitude != null;
    setText('latitude', hasGps ? Number(d.latitude).toFixed(6) : 'Not available');
    setText('longitude', hasGps ? Number(d.longitude).toFixed(6) : 'Not available');
    setText('gpsTag', hasGps ? 'Coordinates received' : 'GPS unavailable');
    setText('gpsMessage', hasGps
      ? 'Location received from the GPS module.'
      : 'Waiting for valid GPS coordinates from ESP32.');

    const mapLink = document.getElementById('mapLink');
    if (hasGps) {
      mapLink.href = 'https://www.google.com/maps?q=' +
        encodeURIComponent(d.latitude + ',' + d.longitude);
      mapLink.style.display = 'inline-block';
    } else {
      mapLink.style.display = 'none';
      mapLink.removeAttribute('href');
    }

    const alerts = [];
    if (d.dry_fill_percent != null && d.dry_fill_percent >= 80)
      alerts.push('Dry waste compartment needs collection.');
    if (d.wet_fill_percent != null && d.wet_fill_percent >= 80)
      alerts.push('Wet waste compartment needs collection.');
    if (overall != null && overall >= 80)
      alerts.push('Overall bin fill is at least 80%.');
    if (alerts.length === 0 && (overall != null ||
        d.dry_fill_percent != null || d.wet_fill_percent != null))
      alerts.push('No collection alert currently.');

    setText('alerts', alerts.join(' '));
    setText('alertCount', alerts.filter(a =>
      a.toLowerCase().includes('needs collection') ||
      a.toLowerCase().includes('at least 80')
    ).length + ' alerts');
  } catch (error) {
    setText('connection', 'Unable to fetch data. Check the Flask server.');
  }
}
refreshData();
setInterval(refreshData, 3000);
</script>
</body>
</html>
"""


def valid_percentage(value):
    if value is None:
        return None
    value = float(value)
    if not 0 <= value <= 100:
        raise ValueError("Fill percentage must be between 0 and 100")
    return round(value, 1)


@app.get("/")
def dashboard():
    return render_template_string(HTML)


@app.get("/api/bin")
def get_bin_data():
    return jsonify(bin_data)


@app.post("/api/bin")
def receive_sensor_data():
    global bin_data

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    try:
        distance = data.get("distance_cm")
        distance = None if distance is None else float(distance)

        if distance is not None and not 0 <= distance <= 400:
            raise ValueError("Distance must be between 0 and 400 cm")

        overall = valid_percentage(data.get("fill_percent"))
        dry = valid_percentage(data.get("dry_fill_percent"))
        wet = valid_percentage(data.get("wet_fill_percent"))

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is not None:
            latitude = float(latitude)
            if not -90 <= latitude <= 90:
                raise ValueError("Invalid latitude")

        if longitude is not None:
            longitude = float(longitude)
            if not -180 <= longitude <= 180:
                raise ValueError("Invalid longitude")

        if (latitude is None) != (longitude is None):
            raise ValueError("Send both latitude and longitude")

    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    # If dry/wet values exist but overall is omitted, use their mean
    # as a simple display estimate, not as a physical measurement.
    if overall is None and dry is not None and wet is not None:
        overall = round((dry + wet) / 2, 1)

    if overall is not None and overall >= 80:
        status = "FULL - COLLECTION NEEDED"
    elif overall is not None and overall >= 60:
        status = "HIGH"
    elif overall is not None and overall >= 30:
        status = "MEDIUM"
    elif overall is not None:
        status = "LOW"
    else:
        status = "WAITING FOR SENSOR"

    bin_data = {
        "distance_cm": distance,
        "fill_percent": overall,
        "dry_fill_percent": dry,
        "wet_fill_percent": wet,
        "latitude": latitude,
        "longitude": longitude,
        "status": status,
        "updated_at": datetime.now().astimezone().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )
    }

    return jsonify({"message": "Sensor data received", "data": bin_data}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
