
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
from pathlib import Path
import sys

app = Flask(__name__)

# Connect Prince's route optimization module
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from route_optimization.optimizer import load_bins, optimize_route


# Latest physical bin sensor data
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

<title>Smart Waste Control Center</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0b1120;
    color: #f4f7ff;
}

main {
    max-width: 1200px;
    margin: auto;
    padding: 30px 20px;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 30px;
}

.logo {
    font-size: 35px;
    margin-right: 12px;
}

.brand {
    display: flex;
    align-items: center;
}

.eyebrow {
    color: #39d98a;
    font-size: 12px;
    letter-spacing: 2px;
    font-weight: bold;
}

h1 {
    font-size: 28px;
    margin: 7px 0;
}

h2 {
    font-size: 18px;
}

.muted, .small {
    color: #9baac2;
    font-size: 13px;
    line-height: 1.6;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
}

.card {
    background: linear-gradient(145deg, #19263c, #111b2c);
    border: 1px solid #293850;
    border-radius: 20px;
    padding: 23px;
    min-width: 0;
    box-shadow: 0 10px 30px #00000020;
}

.wide {
    grid-column: span 2;
}

.full {
    grid-column: 1 / -1;
}

.card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}

.tag {
    background: #26374d;
    color: #b7c6dc;
    padding: 8px 12px;
    border-radius: 30px;
    font-size: 11px;
}

.value {
    font-size: 42px;
    font-weight: bold;
    margin: 15px 0;
}

.track {
    width: 100%;
    height: 11px;
    background: #2c394d;
    border-radius: 20px;
    overflow: hidden;
    margin: 18px 0;
}

.bar {
    height: 100%;
    width: 0%;
    border-radius: 20px;
    transition: width .5s ease;
}

.green {
    background: linear-gradient(90deg, #16b978, #55edaa);
}

.blue {
    background: linear-gradient(90deg, #397be8, #72bcff);
}

.orange {
    background: linear-gradient(90deg, #e89b34, #ffd078);
}

.red {
    background: linear-gradient(90deg, #e34444, #ff7777);
}

.row {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    font-size: 12px;
}

.row span {
    color: #9baac2;
}

.location-box {
    background: #0d1727;
    border: 1px solid #293850;
    border-radius: 15px;
    padding: 18px;
    margin-top: 15px;
}

.coords {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 18px 0;
}

.coord {
    background: #19263c;
    padding: 15px;
    border-radius: 12px;
    overflow-wrap: anywhere;
}

.coord label {
    display: block;
    color: #9baac2;
    font-size: 11px;
    margin-bottom: 9px;
}

button, .map-link {
    display: inline-block;
    padding: 12px 17px;
    border: 0;
    border-radius: 10px;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;
    font-size: 13px;
}

button {
    background: #39d98a;
    color: #071a17;
}

.map-link {
    background: #263e5c;
    color: white;
}

button:hover, .map-link:hover {
    opacity: .8;
}

.route-item {
    background: #0d1727;
    padding: 15px;
    margin: 10px 0;
    border-radius: 12px;
    border: 1px solid #293850;
}

.alert {
    color: #ffbd69;
    line-height: 1.7;
}

.footer {
    text-align: center;
    margin-top: 30px;
    color: #7889a3;
    font-size: 12px;
}

@media(max-width: 750px) {
    .grid {
        grid-template-columns: 1fr;
    }

    .wide, .full {
        grid-column: auto;
    }

    main {
        padding: 20px 13px;
    }
}
</style>
</head>

<body>

<main>

<header>
    <div class="brand">
        <div class="logo">♻️</div>
        <div>
            <div class="eyebrow">IOT WASTE MANAGEMENT</div>
            <h1>Smart Waste Control Center</h1>
            <div class="small">Live Monitoring and Route Optimization</div>
        </div>
    </div>

    <div class="tag">
        ● BIN-001 | PHYSICAL BIN
    </div>
</header>


<div class="grid">

    <!-- Overall Fill -->
    <section class="card">
        <div class="card-head">
            <h2>♻ Overall Fill</h2>
            <span class="tag" id="overallTag">Waiting</span>
        </div>

        <div class="small">Total bin fill level</div>

        <div class="value">
            <span id="overall">--</span>%
        </div>

        <div class="track">
            <div class="bar green" id="overallBar"></div>
        </div>

        <div class="row">
            <span>Status</span>
            <strong id="overallStatus">Waiting</strong>
        </div>
    </section>


    <!-- Dry Waste -->
    <section class="card">
        <div class="card-head">
            <h2>🟢 Dry Waste</h2>
            <span class="tag">Compartment A</span>
        </div>

        <div class="small">Paper, plastic and dry waste</div>

        <div class="value">
            <span id="dry">--</span>%
        </div>

        <div class="track">
            <div class="bar green" id="dryBar"></div>
        </div>

        <div class="row">
            <span>Fill status</span>
            <strong id="dryStatus">No reading</strong>
        </div>
    </section>


    <!-- Wet Waste -->
    <section class="card">
        <div class="card-head">
            <h2>🔵 Wet Waste</h2>
            <span class="tag">Compartment B</span>
        </div>

        <div class="small">Food scraps and wet waste</div>

        <div class="value">
            <span id="wet">--</span>%
        </div>

        <div class="track">
            <div class="bar blue" id="wetBar"></div>
        </div>

        <div class="row">
            <span>Fill status</span>
            <strong id="wetStatus">No reading</strong>
        </div>
    </section>


    <!-- GPS -->
    <section class="card wide">
        <div class="card-head">
            <h2>📍 GPS Location</h2>
            <span class="tag" id="gpsTag">GPS unavailable</span>
        </div>

        <div class="location-box">

            <div class="small">
                Physical waste bin location
            </div>

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

            <a id="mapLink"
               class="map-link"
               href="#"
               target="_blank"
               rel="noopener noreferrer"
               style="display:none">
               Open Google Maps ↗
            </a>

            <p class="small" id="gpsMessage">
                Waiting for GPS coordinates.
            </p>

        </div>
    </section>


    <!-- Sensor Details -->
    <section class="card">
        <div class="card-head">
            <h2>📡 Sensor Details</h2>
            <span class="tag">Live</span>
        </div>

        <div class="small">Average sensor distance</div>

        <div class="value">
            <span id="distance">--</span>
            <span style="font-size:16px">cm</span>
        </div>

        <div class="row">
            <span>Last update</span>
            <strong id="updated">Not received</strong>
        </div>

        <p class="small" id="connection">
            Waiting for ESP32 data.
        </p>

        <button onclick="refreshData()">Refresh Data</button>
    </section>


    <!-- Route Optimization -->
    <section class="card full">

        <div class="card-head">
            <div>
                <h2>🚛 Smart Collection Route</h2>
                <div class="small">
                    Suggested route for garbage collection
                </div>
            </div>

            <span class="tag" id="routeCount">
                Loading...
            </span>
        </div>

        <div id="routeList" class="small">
            Loading optimized route...
        </div>

        <p class="small">
            Total estimated straight-line distance:
            <strong id="routeDistance">-- km</strong>
        </p>

        <button onclick="refreshRoute()">
            Refresh Route
        </button>

    </section>


    <!-- Alerts -->
    <section class="card full">

        <div class="card-head">
            <h2>⚠ Collection Alerts</h2>
            <span class="tag" id="alertCount">0 alerts</span>
        </div>

        <p class="alert" id="alerts">
            Waiting for sensor readings.
        </p>

    </section>

</div>

<div class="footer">
    SMART WASTE MANAGEMENT SYSTEM
    <br>
    ESP32 · ULTRASONIC · GPS · FLASK · ROUTE OPTIMIZATION
</div>

</main>


<script>

function setText(id, value) {
    document.getElementById(id).textContent = value;
}

function formatFill(value) {
    if (value === null || value === undefined) {
        return "--";
    }

    return Number(value).toFixed(1);
}

function fillStatus(value) {
    if (value === null || value === undefined) {
        return "No reading";
    }

    if (value >= 80) return "Collection Needed";
    if (value >= 60) return "High";
    if (value >= 30) return "Medium";

    return "Low";
}

function setFill(id, value, color) {
    const bar = document.getElementById(id);

    const percentage = value === null || value === undefined
        ? 0
        : Math.max(0, Math.min(100, Number(value)));

    bar.style.width = percentage + "%";
    bar.className = "bar " + color;
}


async function refreshData() {

    try {

        const response = await fetch("/api/bin");

        if (!response.ok) {
            throw new Error("API unavailable");
        }

        const d = await response.json();

        // Overall fill
        setText("overall", formatFill(d.fill_percent));
        setText("overallStatus", fillStatus(d.fill_percent));
        setText("overallTag", fillStatus(d.fill_percent));

        setFill(
            "overallBar",
            d.fill_percent,
            d.fill_percent >= 80 ? "red" : "green"
        );

        // Dry waste
        setText("dry", formatFill(d.dry_fill_percent));
        setText("dryStatus", fillStatus(d.dry_fill_percent));
        setFill("dryBar", d.dry_fill_percent, "green");

        // Wet waste
        setText("wet", formatFill(d.wet_fill_percent));
        setText("wetStatus", fillStatus(d.wet_fill_percent));
        setFill("wetBar", d.wet_fill_percent, "blue");

        // Sensor
        setText(
            "distance",
            d.distance_cm == null ? "--" : d.distance_cm
        );

        setText("updated", d.updated_at);

        setText(
            "connection",
            d.fill_percent == null &&
            d.dry_fill_percent == null &&
            d.wet_fill_percent == null
                ? "Waiting for ESP32 data."
                : "Latest sensor data received."
        );

        // GPS
        const hasGPS =
            d.latitude !== null &&
            d.longitude !== null;

        setText(
            "latitude",
            hasGPS ? Number(d.latitude).toFixed(6) : "Not available"
        );

        setText(
            "longitude",
            hasGPS ? Number(d.longitude).toFixed(6) : "Not available"
        );

        setText(
            "gpsTag",
            hasGPS ? "GPS Connected" : "GPS unavailable"
        );

        setText(
            "gpsMessage",
            hasGPS
                ? "Location received from GPS module."
                : "Waiting for valid GPS coordinates."
        );

        const mapLink = document.getElementById("mapLink");

        if (hasGPS) {

            mapLink.href =
                "https://www.google.com/maps?q=" +
                encodeURIComponent(d.latitude + "," + d.longitude);

            mapLink.style.display = "inline-block";

        } else {

            mapLink.style.display = "none";
            mapLink.removeAttribute("href");

        }

        // Alerts
        const alerts = [];

        if (d.dry_fill_percent != null &&
            d.dry_fill_percent >= 80) {
            alerts.push("Dry waste compartment needs collection.");
        }

        if (d.wet_fill_percent != null &&
            d.wet_fill_percent >= 80) {
            alerts.push("Wet waste compartment needs collection.");
        }

        if (d.fill_percent != null &&
            d.fill_percent >= 80) {
            alerts.push("Overall bin is nearly full.");
        }

        if (alerts.length === 0 &&
            (d.fill_percent != null ||
             d.dry_fill_percent != null ||
             d.wet_fill_percent != null)) {
            alerts.push("No collection alert currently.");
        }

        if (alerts.length === 0) {
            alerts.push("Waiting for sensor readings.");
        }

        setText("alerts", alerts.join(" "));
        setText("alertCount", alerts.length + " alerts");

    } catch (error) {

        setText(
            "connection",
            "Unable to fetch data. Check Flask server."
        );

    }
}


// Prince's Route Optimization API
async function refreshRoute() {

    const routeList = document.getElementById("routeList");

    try {

        const response = await fetch("/api/route");

        if (!response.ok) {
            throw new Error("Route API unavailable");
        }

        const data = await response.json();

        setText("routeCount", data.bins_to_collect + " bins");

        setText(
            "routeDistance",
            data.total_distance_km + " km"
        );

        routeList.replaceChildren();

        if (data.route.length === 0) {

            routeList.textContent =
                "No bins meet the collection threshold.";

            return;
        }

        data.route.forEach((bin, index) => {

            const item = document.createElement("div");
            item.className = "route-item";

            const heading = document.createElement("strong");

            heading.textContent =
                (index + 1) + ". " +
                bin.bin_id + " - " +
                bin.fill_percent + "% full";

            const details = document.createElement("p");
            details.className = "small";

            details.textContent =
                "Distance from previous stop: " +
                bin.distance_from_previous_km + " km";

            item.append(heading, details);
            routeList.appendChild(item);

        });

    } catch (error) {

        routeList.textContent =
            "Route unavailable. Check route optimization module.";

        setText("routeCount", "Unavailable");

    }
}


// Automatic updates
refreshData();
refreshRoute();

setInterval(refreshData, 3000);
setInterval(refreshRoute, 10000);

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
        return jsonify({"error": "Expected JSON object"}), 400

    try:

        distance = data.get("distance_cm")

        if distance is not None:
            distance = float(distance)

            if not 0 <= distance <= 400:
                raise ValueError("Invalid distance")

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
            raise ValueError("Send both GPS coordinates")

        if overall is None and dry is not None and wet is not None:
            overall = round((dry + wet) / 2, 1)

    except (TypeError, ValueError) as error:

        return jsonify({"error": str(error)}), 400

    if overall is None:
        status = "WAITING FOR SENSOR"
    elif overall >= 80:
        status = "FULL"
    elif overall >= 60:
        status = "HIGH"
    elif overall >= 30:
        status = "MEDIUM"
    else:
        status = "LOW"

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

    return jsonify({
        "message": "Sensor data received",
        "data": bin_data
    }), 200


# Route optimization API
@app.get("/api/route")
def get_optimized_route():

    try:

        bins = load_bins()

        result = optimize_route(
            bins,
            depot_lat=27.4920,
            depot_lon=77.6730,
            threshold=60
        )

        return jsonify({
            "route": result["route"],
            "total_distance_km": result["total_distance_km"],
            "bins_to_collect": result["bins_to_collect"],
            "threshold_percent": result["threshold_percent"]
        })

    except (FileNotFoundError, ValueError) as error:

        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
