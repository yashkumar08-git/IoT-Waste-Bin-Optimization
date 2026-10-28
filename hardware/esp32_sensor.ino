#define TRIG_PIN 5
#define ECHO_PIN 18

// Change these values after measuring your actual bin.
const float BIN_EMPTY_DISTANCE_CM = 30.0;
const float BIN_FULL_DISTANCE_CM  = 3.0;

const float SOUND_SPEED_CM_US = 0.0343;

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);

  if (duration == 0) {
    return -1.0;
  }

  return (duration * SOUND_SPEED_CM_US) / 2.0;
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  digitalWrite(TRIG_PIN, LOW);

  Serial.println("Smart Waste Bin - Fill Level Monitor");
}

void loop() {
  float distance = readDistanceCm();

  if (distance < 0) {
    Serial.println("ERROR: No echo. Check sensor wiring.");
    delay(1000);
    return;
  }

  // Clamp readings to the usable range.
  float fillPercent =
      (BIN_EMPTY_DISTANCE_CM - distance) /
      (BIN_EMPTY_DISTANCE_CM - BIN_FULL_DISTANCE_CM) * 100.0;

  if (fillPercent < 0) fillPercent = 0;
  if (fillPercent > 100) fillPercent = 100;

  const char* status;

  if (fillPercent >= 80) {
    status = "FULL / COLLECTION NEEDED";
  } else if (fillPercent >= 60) {
    status = "HIGH";
  } else if (fillPercent >= 30) {
    status = "MEDIUM";
  } else {
    status = "LOW";
  }

  Serial.print("Distance: ");
  Serial.print(distance, 1);
  Serial.println(" cm");

  Serial.print("Fill Level: ");
  Serial.print(fillPercent, 1);
  Serial.println("%");

  Serial.print("Bin Status: ");
  Serial.println(status);

  Serial.println("-------------------------");
  delay(1500);
}