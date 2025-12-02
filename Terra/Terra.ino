#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX (blau, taronja)

// Definició LED recepció
const int led = 12;
bool stateLed = LOW;

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);

  pinMode (led, OUTPUT);
}

// Falta codi que no funciona actualment pero que tenim escrit

void loop() {
  if (mySerial.available()) {//Sat para python
    digitalWrite(led, HIGH);

    String comando = mySerial.readStringUntil('\n'); //Rebre
    Serial.println(comando); //Enviar
    
    digitalWrite(led, LOW);
  }
  
  if(Serial.available()){
    //Python para sat
    String info = Serial.readStringUntil('\n');
    mySerial.println(info);
  }
}