#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX (blau, taronja)

// Definició LED recepció
const int led = 12;
bool stateLed = LOW;

// Definició Alarma
const int alarma = 13;
bool stateAlarma = LOW;

bool esperantTimeout = false;
long NextMillisTIMEOUT;
int PeriodeTIMEOUT = 5000;

void setup() {
  pinMode (led, OUTPUT);
  pinMode (alarma, OUTPUT);

  Serial.begin(9600);
  mySerial.begin(9600);

  NextMillisTIMEOUT = PeriodeTIMEOUT;
}

//--------------------------------------------------
// Definició de les funcions
//--------------------------------------------------

void ProcessarCom(String comando) {
  comando.trim();
  int fin = comando.indexOf(':', 0);
  int codigo = comando.substring(0, fin).toInt();
  int inicio = fin + 1;

  if (codigo == 3) { // Alarma sensor DHT
    stateAlarma = HIGH;
    digitalWrite(alarma, stateAlarma);
  }
  else{
    stateAlarma = LOW;
    digitalWrite(alarma, stateAlarma);
  }
}
//--------------------------------------------------
// Programa prinicipal
//--------------------------------------------------

void loop() {
  if (mySerial.available()) {//Sat para python
    digitalWrite(led, HIGH);
    NextMillisTIMEOUT = millis() + PeriodeTIMEOUT;

    String comando = mySerial.readStringUntil('\n'); //Rebre
    Serial.println(comando); //Enviar
      
    ProcessarCom(comando);//
    digitalWrite(led, LOW);
  }
  else{
    if (millis()>= NextMillisTIMEOUT){
      Serial.println("4:");
    }
  }

  if(Serial.available()){
    //Python para sat
    String info = Serial.readString();
    mySerial.println(info);
  }
}