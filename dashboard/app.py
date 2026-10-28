
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

bin_data = {
    "distance_cm": None,
    "fill_percent": 0,
    "status": "WAITING FOR SENSOR",
    "updated_at": "No readings received yet"
}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Smart Waste Bin</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0; padding: 28px 16px;
  font-family: Arial, sans-serif;
  background: #f3f5fa; color: #20243a;
}
main { max-width: 760px; margin: auto; }
header { margin-bottom: 24px; }
h1 { margin-bottom: 8px; }
.muted { color: #687087; }
.card {
  background: white; border-radius: 18px;
  padding: 24px; margin-bottom: 18px;
  box-shadow: 0 5px 20px #17255412;
}
.label { color: #687087; font-size: 14px; }
.value { font-size: 42px; font-weight: bold; margin: 12px 0; }
.track {
  height: 14px; background: #e7eaf1;
  border-radius: 10px; overflow: hidden;
}
#bar {
  height: 100%; width: 0%;
  background: #219653; transition: width .4s;
}
.status {
  display: inline-block; padding: 9px 13px;
  background: #e8f7ee; border-radius: 20px;
  font-weight: bold; margin-top: 14px;
}
button {
  border: 0; border-radius: 10px; padding: 12px 18px;
  background: #343b80; color: white; cursor: pointer;
}
</style>
</head>
<body>
<main>
  <header>
    <p class="muted">IoT WASTE MANAGEMENT</p>
    <h1>Smart Waste Bin Dashboard</h1>
    <p class="muted">One physical bin · Live fill-level monitoring</p>
  </header>

  <section class="card">
    <div class="label">BIN FILL LEVEL</div>
    <div class="value"><span id="fill">0</span>%</div>
    <div class="track"><div id="bar"></div></div>
    <div id="status" class="status">WAITING FOR SENSOR</div>
  </section>

  <section class="card">
    <h3>Sensor Details</h3>
    <p>Distance: <strong id="distance">--</strong> cm</p>
    <p>Last update: <span id="updated">No readings received yet</span></p>
    <p id="alert" class="muted">Waiting for ESP32 data.</p>
    <button onclick="refreshData()">Refresh now</button>
  </section>
</main>

<script>
async function refreshData() {
  try {
    const response = await fetch('/api/bin');
    if (!response.ok) throw new Error('API unavailable');

    const d = await response.json();
    document.getElementById('fill').textContent = d.fill_percent;
    document.getElementById('bar').style.width = d.fill_percent + '%';
    document.getElementById('distance').textContent =
      d.distance_cm === null ? '--' : d.distance_cm;
    document.getElementById('status').textContent = d.status;
    document.getElementById('updated').textContent = d.updated_at;

    document.getElementById('bar').style.background =
      d.fill_percent >= 80 ? '#d93025' :
      d.fill_percent >= 60 ? '#e6a700' : '#219653';

    document.getElementById('alert').textContent =
      d.fill_percent >= 80 ? 'Collection needed: bin is nearly full!' :
      d.status === 'WAITING FOR SENSOR' ? 'Waiting for ESP32 data.' :
      'No collection alert currently.';
  } catch (error) {
    document.getElementById('alert').textContent =
      'Could not refresh data. Check the Flask server.';
  }
}
refreshData();
setInterval(refreshData, 3000);
</script>
</body>
</html>
"""


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
        return jsonify({"error": "Expected JSON"}), 400

    try:
        distance = float(data["distance_cm"])
        fill = float(data["fill_percent"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Invalid sensor values"}), 400

    if not (0 <= distance <= 400 and 0 <= fill <= 100):
        return jsonify({"error": "Values outside valid range"}), 400

    if fill >= 80:
        status = "FULL - COLLECTION NEEDED"
    elif fill >= 60:
        status = "HIGH"
    elif fill >= 30:
        status = "MEDIUM"
    else:
        status = "LOW"

    bin_data = {
        "distance_cm": round(distance, 1),
        "fill_percent": round(fill, 1),
        "status": status,
        "updated_at": datetime.now().astimezone().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )
    }

    return jsonify({"message": "Sensor data received"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
