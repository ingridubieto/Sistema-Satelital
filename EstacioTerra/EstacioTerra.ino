#include <SoftwareSerial.h>
#include <Servo.h>
#include <NewPing.h>

SoftwareSerial mySerial(10, 11); // RX, TX (blau, taronja)

// Definició LED recepció
const int led = 12;
bool stateLed = LOW;

// Definició Alarma
const int alarma = 13;
bool stateAlarma = LOW;

//int pinJoystick = A0;

//int llegirJoystick() {
  //int valor = analogRead(pinJoystick); // 0-1023
  //int angle = map(valor, 0, 1023, 0, 180); // Convertim a graus
  //return angle; // Retornem el resultat
//}

void deteccioError (){
   String data = mySerial.readString();
   //Serial.print(data);
   data.trim();
   if (data == "Fallo"){
      stateAlarma = HIGH;
   }
   else{
         stateAlarma = LOW;
         }
   digitalWrite(alarma, stateAlarma);
}

int obtenirDistancia() {
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
   pinMode (led, OUTPUT);
   pinMode (alarma, OUTPUT);
   pinMode (alarmaSensor, OUTPUT);

   Serial.begin(9600);
   mySerial.begin(9600);

   nextMillisSENSOR = millis() + 1000;
}

void loop() {
   if (mySerial.available()) {
      encendreLeds();
      deteccioError();
      int angle = llegirJoystick(); // cridem funció
      moureServo(angle);            // cridem funció
      delay(100);
      if (millis() >= nextMillisSENSOR){
         int distancia = obtenirDistancia();
         mostrarDistancia(distancia);
         nextMillisSENSOR = millis() + 1000;
      }
   }
}