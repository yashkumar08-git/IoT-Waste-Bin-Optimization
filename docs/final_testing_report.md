
# Smart Waste Bin – Final Testing Report

## 1. Project Overview
IoT Smart Waste Bin Fill-Level & Route Optimization Engine monitors waste levels using ESP32 and ultrasonic sensors. GPS provides location information, while the software suggests a collection route.

## 2. Technology Stack
- ESP32
- HC-SR04 Ultrasonic Sensor
- GPS Module
- Python
- Flask
- HTML, CSS and JavaScript
- Route Optimization Algorithm

## 3. Software Testing

| Test Case | Expected Result | Actual Result |
|---|---|---|
| Dashboard loading | Dashboard opens | Pending |
| Sensor API | Accepts valid JSON | Pending |
| Dry waste monitoring | Displays fill percentage | Pending |
| Wet waste monitoring | Displays fill percentage | Pending |
| GPS location | Displays coordinates | Pending |
| Route API | Returns collection route | Pending |
| Invalid sensor data | Returns error | Pending |

## 4. Hardware Testing

| Test | Expected Result | Actual Result |
|---|---|---|
| ESP32 connection | Board detected | Pending |
| Ultrasonic sensor | Measures distance | Pending |
| GPS module | Provides valid coordinates | Pending |
| Wi-Fi connection | ESP32 connects | Pending |
| Dashboard integration | Receives live data | Pending |

## 5. Limitations
- Additional bin locations are simulated in software.
- Route optimization uses straight-line GPS distance, not actual road distance.
- GPS accuracy depends on satellite availability.
- Real-time monitoring requires an active Wi-Fi connection.

## 6. Conclusion
The project combines IoT-based waste monitoring, GPS location tracking, dashboard visualization and software-based route optimization to support smarter waste collection.
