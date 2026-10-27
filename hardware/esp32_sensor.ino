
#define TRIG_PIN 5
#define ECHO_PIN 18

const float SOUND_SPEED_CM_US = 0.0343;

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  digitalWrite(TRIG_PIN, LOW);
  delay(500);

  Serial.println("Smart Waste Bin - Sensor Test");
  Serial.println("Distance readings in cm");
}

void loop() {
  // Send a 10-microsecond trigger pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Wait for echo; timeout after 30 ms
  unsigned long duration =
      pulseIn(ECHO_PIN, HIGH, 30000UL);

  if (duration == 0) {
    Serial.println("No echo - check wiring and sensor");
  } else {
    float distance =
        (duration * SOUND_SPEED_CM_US) / 2.0;

    // HC-SR04's practical range is approximately 2-400 cm
    if (distance >= 2.0 && distance <= 400.0) {
      Serial.print("Distance: ");
      Serial.print(distance, 1);
      Serial.println(" cm");
    } else {
      Serial.println("Reading outside expected range");
    }
  }

  delay(1000);
}
