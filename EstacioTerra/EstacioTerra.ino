#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX (blau, taronja)

// Definició LED recepció
const int led = 12;
bool stateLed = LOW;

// Definició Alarma
const int alarma = 13;
bool stateAlarma = LOW;

<<<<<<< HEAD
//int pinJoystick = A0;

=======
bool esperantTimeout = false;
long NextMillisTIMEOUT;
int PeriodeTIMEOUT = 5000;
>>>>>>> 2ef52181992715da1912a1e5111921867cd3ff12
//int llegirJoystick() {
  //int valor = analogRead(pinJoystick); // 0-1023
  //int angle = map(valor, 0, 1023, 0, 180); // Convertim a graus
  //return angle; // Retornem el resultat
//}

void setup() {
  pinMode (led, OUTPUT);
  pinMode (alarma, OUTPUT);

  Serial.begin(9600);
  mySerial.begin(9600);

  NextMillisTIMEOUT = millis();

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

<<<<<<< HEAD
void setup() {
   pinMode (led, OUTPUT);
   pinMode (alarma, OUTPUT);
   pinMode (alarmaSensor, OUTPUT);

   Serial.begin(9600);
   mySerial.begin(9600);

   nextMillisSENSOR = millis() + 1000;
}
=======
//--------------------------------------------------
// Programa prinicipal
//--------------------------------------------------
>>>>>>> 2ef52181992715da1912a1e5111921867cd3ff12

void loop() {
  if (mySerial.available()) {//Sat para python   
    digitalWrite(led, HIGH);
    NextMillisTIMEOUT = millis() + PeriodeTIMEOUT;

    String comando = Serial.readString(); //Rebre
    mySerial.println(comando); //Enviar
      
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
    String info = mySerial.readString();
    Serial.println(info);
  }
}