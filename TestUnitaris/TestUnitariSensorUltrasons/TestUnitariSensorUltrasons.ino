#include <NewPing.h>

long nextMillisSENSOR = 1000;
const int UltrasonicPin = 5;
const int MaxDistance = 200;
const int alarmaSensor = 7;

NewPing sonar(UltrasonicPin, UltrasonicPin, MaxDistance);

int obtenerDistancia() {
  int distancia = sonar.ping_cm();
  return distancia;
}

void mostrarDistancia(int distancia) {
  if (distancia == 0){
    Serial.println("Fuera de rango");
    digitalWrite(alarmaSensor, HIGH);
    delay(500);
    digitalWrite(alarmaSensor, LOW);
    delay(500);
  }
  else{
    Serial.print(distancia);
    Serial.println(" cm");
  }
}

void setup() {
  Serial.begin(9600);
  nextMillisSENSOR = millis() + 1000;
  pinMode (alarmaSensor, OUTPUT);
}

void loop() {
  if (millis() >= nextMillisSENSOR){
    int distancia = obtenerDistancia();
    mostrarDistancia(distancia);
    nextMillisSENSOR = millis() + 1000;
  }
}