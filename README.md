
# IoT Smart Waste Bin Fill-Level & Route Optimization Engine

An IoT-based smart waste management system that monitors waste fill levels, tracks bin location using GPS, and suggests an optimized collection route.

## Project Overview

The system uses ESP32, ultrasonic sensors and GPS to monitor waste levels and location.

A Flask dashboard displays sensor readings, dry and wet waste levels, GPS coordinates and collection alerts.

Additional bin locations are simulated in software to demonstrate route optimization.

## Key Features

- Real-time waste fill-level monitoring
- Separate dry and wet waste monitoring
- GPS-based bin location tracking
- Google Maps location link
- Flask web dashboard
- Automatic collection alerts
- Software-based route optimization
- REST API for ESP32 communication

## Technology Stack

| Component | Technology |
|---|---|
| Microcontroller | ESP32 |
| Distance Sensor | HC-SR04 |
| GPS | GPS Module |
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Route Optimization | Python |
| Data Storage | CSV |

## Project Structure

```text
IoT-Waste-Bin-Optimization/
│
├── hardware/
│   ├── esp32_sensor.ino
│   └── test_results/
│       └── final_hardware_test.md
│
├── dashboard/
│   ├── app.py
│   └── requirements.txt
│
├── route_optimization/
│   ├── optimizer.py
│   └── test_routes.py
│
├── data/
│   └── sample_bins.csv
│
├── docs/
│   ├── project_synopsis.md
│   ├── final_testing_report.md
│   └── demo_photos/
│
└── README.md
```

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yashkumar08-git/IoT-Waste-Bin-Optimization.git
cd IoT-Waste-Bin-Optimization
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r dashboard/requirements.txt
```

## Run Dashboard

```bash
python dashboard/app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/api/bin` | Current sensor readings |
| POST | `/api/bin` | Receive ESP32 data |
| GET | `/api/route` | Optimized collection route |

## Sensor Data Format

ESP32 sends JSON data to the Flask API.

```json
{
  "distance_cm": 12.5,
  "fill_percent": 65,
  "dry_fill_percent": 80,
  "wet_fill_percent": 50,
  "latitude": 27.4924,
  "longitude": 77.6737
}
```

## Route Optimization

The software:
1. Loads simulated bin locations from CSV.
2. Selects bins above a configurable fill threshold.
3. Calculates straight-line GPS distances.
4. Creates a collection sequence using a greedy heuristic.

Note: The generated route is not a guaranteed shortest road route.

## Hardware Requirements

- ESP32 development board
- HC-SR04 ultrasonic sensors
- GPS module
- Connecting wires
- Voltage divider resistors
- Waste bin compartments

## Project Limitations

- Only one physical bin is used in the prototype.
- Additional bin locations are simulated.
- Actual GPS readings require a valid satellite fix.
- Live monitoring requires Wi-Fi connectivity.
- Route distance is calculated using straight-line coordinates.

## Team Contributions

- Yash Porwal: Dashboard development and backend integration.
- Samarth Gupta: ESP32 hardware and sensor firmware.
- Prince Raikwar: Route optimization and algorithm testing.

## Future Scope

- Multiple physical smart bins
- Cloud database integration
- Road-network-based route optimization
- Waste collection vehicle tracking
- Mobile application
- Historical waste analytics

## Project Conclusion

The project demonstrates how IoT, GPS tracking, web technologies and route optimization can be combined to improve waste monitoring and collection planning.
