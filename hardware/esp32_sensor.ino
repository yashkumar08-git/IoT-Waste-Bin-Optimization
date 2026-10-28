#include <WiFi.h>
#include <HTTPClient.h>

// HC-SR04 wiring
#define TRIG_PIN 5
#define ECHO_PIN 18

// Replace with actual measurements of your bin.
const float BIN_EMPTY_DISTANCE_CM = 30.0;
const float BIN_FULL_DISTANCE_CM = 3.0;

const float SOUND_SPEED_CM_US = 0.0343;

// Configure these locally. Never commit real credentials.
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Replace with the laptop's IPv4 address.
const char* SERVER_URL =
    "http://192.168.1.5:5000/api/bin";

unsigned long lastReconnectAttempt = 0;

float readDistanceOnce() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration =
      pulseIn(ECHO_PIN, HIGH, 30000UL);

  if (duration == 0) {
    return -1.0;
  }

  float distance =
      (duration * SOUND_SPEED_CM_US) / 2.0;

  if (distance < 2.0 || distance > 400.0) {
    return -1.0;
  }

  return distance;
}

float readMedianDistance() {
  float readings[5];
  int count = 0;

  for (int i = 0; i < 5; i++) {
    float value = readDistanceOnce();

    if (value >= 2.0 && value <= 400.0) {
      readings[count++] = value;
    }

    delay(60);
  }

  // Require at least 3 valid readings.
  if (count < 3) {
    return -1.0;
  }

  // Sort valid readings.
  for (int i = 0; i < count - 1; i++) {
    for (int j = i + 1; j < count; j++) {
      if (readings[j] < readings[i]) {
        float temp = readings[i];
        readings[i] = readings[j];
        readings[j] = temp;
      }
    }
  }

  return readings[count / 2];
}

float calculateFillPercent(float distance) {
  float fill =
      (BIN_EMPTY_DISTANCE_CM - distance) /
      (BIN_EMPTY_DISTANCE_CM - BIN_FULL_DISTANCE_CM)
      * 100.0;

  return constrain(fill, 0.0, 100.0);
}

const char* getBinStatus(float fill) {
  if (fill >= 80.0) return "FULL";
  if (fill >= 60.0) return "HIGH";
  if (fill >= 30.0) return "MEDIUM";
  return "LOW";
}

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  if (millis() - lastReconnectAttempt < 10000UL) {
    return;
  }

  lastReconnectAttempt = millis();

  Serial.println("Connecting to Wi-Fi...");
  WiFi.disconnect();
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void sendToDashboard(float distance, float fill) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi unavailable; upload skipped.");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  http.setTimeout(3000);

  if (!http.begin(client, SERVER_URL)) {
    Serial.println("Could not initialize HTTP client.");
    return;
  }

  http.addHeader("Content-Type", "application/json");

  String body =
      "{\"distance_cm\":" + String(distance, 1) +
      ",\"fill_percent\":" + String(fill, 1) + "}";

  int responseCode = http.POST(body);

  Serial.print("HTTP response: ");
  Serial.println(responseCode);

  if (responseCode > 0) {
    Serial.println(http.getString());
  } else {
    Serial.println(http.errorToString(responseCode));
  }

  http.end();
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.println("Smart Waste Bin starting...");
}

void loop() {
  connectWiFi();

  float distance = readMedianDistance();

  if (distance < 0) {
    Serial.println("ERROR: Insufficient valid readings.");
    delay(2000);
    return;
  }

  float fill = calculateFillPercent(distance);

  Serial.printf("Distance: %.1f cm\n", distance);
  Serial.printf("Fill level: %.1f%%\n", fill);
  Serial.printf("Status: %s\n", getBinStatus(fill));

  sendToDashboard(distance, fill);

  Serial.println("--------------------------");
  delay(5000);
}