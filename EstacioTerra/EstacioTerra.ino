#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)
unsigned long nextMillis = 500;
const int led = 12;
bool stateLed = LOW;
const int alarma = 13;
bool stateAlarma = LOW;
void setup() {
   pinMode (led, OUTPUT);
   pinMode (alarma, OUTPUT);
   Serial.begin(9600);
   mySerial.begin(9600);
}
void loop() {
   if (mySerial.available()) {
      stateLed = HIGH;
      digitalWrite (led, stateLed);
      String data = mySerial.readString();
      Serial.print(data);
      stateLed = LOW;
      digitalWrite (led, stateLed);
      data.trim();
      if (data == "Fallo"){
         stateAlarma = HIGH;
      }
      else{
         stateAlarma = LOW;
      }
      digitalWrite (alarma, stateAlarma);
   }
}