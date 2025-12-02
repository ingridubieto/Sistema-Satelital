#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX (blau, taronja)

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
}

void loop() {
  if (mySerial.available()) {//Sat para python
    String comando = mySerial.readStringUntil('\n'); //Rebre
    Serial.println(comando); //Enviar
  }
  
  if(Serial.available()){
    //Python para sat
    String info = Serial.readStringUntil('\n');
    mySerial.println(info);
  }
}