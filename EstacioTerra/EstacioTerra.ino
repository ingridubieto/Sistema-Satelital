#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)
unsigned long nextMillis = 500;
const int led = 12;
bool stateLed = LOW;
bool stateAlarma = LOW;
const int alarma = 13;
void setup() {
   pinMode (led, OUTPUT);
   Serial.begin(9600);
   mySerial.begin(9600);
}
void loop() {
   if (mySerial.available()) {
      stateLed = HIGH;
      digitalWrite (led, stateLed);
      String data = mySerial.readString();
      String paraula = String data.trim();
      Serial.print(data);
      stateLed = LOW;
      digitalWrite (led, stateLed);
      if (paraula == 'Fallo'){
         stateAlarma = HIGH;
         digitalWrite (alarma, stateAlarma);
      }
      else{
         stateAlarma = LOW;
         digitalWrite (alarma, stateAlarma);
      }

   }
}