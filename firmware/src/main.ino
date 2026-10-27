
const int TRIG_PIN = 5;
const int ECHO_PIN = 18;

// Measure the internal height of your actual bin in centimeters.
const float BIN_HEIGHT_CM = 40.0;

const float FULL_THRESHOLD = 80.0;
const float MEDIUM_THRESHOLD = 50.0;

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(3);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Timeout avoids waiting indefinitely if no echo is received.
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);

  if (duration == 0) {
    return -1.0; // Invalid reading / timeout
  }

  return duration * 0.0343 / 2.0;
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  digitalWrite(TRIG_PIN, LOW);

  Serial.println("IoT Smart Waste Bin - Sensor Test");
}

void loop() {
  float distanceCm = readDistanceCm();

  if (distanceCm < 0 ||
      distanceCm > BIN_HEIGHT_CM) {
    Serial.println("Invalid reading: check sensor, wiring or bin dimensions.");
    delay(1000);
    return;
  }

  float fillLevel =
      ((BIN_HEIGHT_CM - distanceCm) / BIN_HEIGHT_CM) * 100.0;

  fillLevel = constrain(fillLevel, 0.0, 100.0);

  const char* status;

  if (fillLevel >= FULL_THRESHOLD) {
    status = "FULL";
  } else if (fillLevel >= MEDIUM_THRESHOLD) {
    status = "MEDIUM";
  } else {
    status = "LOW";
  }

  Serial.print("distanceCm: ");
  Serial.print(distanceCm, 1);

  Serial.print(" | fillLevel: ");
  Serial.print(fillLevel, 1);
  Serial.print("%");

  Serial.print(" | status: ");
  Serial.println(status);

  delay(2000);
}
