#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX (blau, taronja)

// Definició LED recepció
const int led = 12;
bool stateLed = LOW;

//Definicio Alarma Sonora
const int buzzer = 9;

// Definició Alarma
const int alarma = 13;
bool stateAlarma = LOW;

bool esperantTimeout = false;
long NextMillisTIMEOUT;
int PeriodeTIMEOUT = 5000;
bool Comunicacio = true;

// Definicio Joystick
bool MANUAL = false;
unsigned long NextMillisJoystick = 20;
const int PeriodeJoystick = 50; // ms entre envíos
const int joyX = A0;

void setup() {
  pinMode (led, OUTPUT);
  pinMode (alarma, OUTPUT);
  pinMode(buzzer, OUTPUT);

  Serial.begin(9600);
  mySerial.begin(9600);

  NextMillisTIMEOUT = PeriodeTIMEOUT;
}

//--------------------------------------------------
// Definició de les funcions
//--------------------------------------------------

String AfegirChecksum(String paraula){
  return paraula + "|" + String(Checksum(paraula));
}

void ProcessarCom(String comando) {
  comando.trim();
  int fin = comando.indexOf(':', 0);
  int codigo = comando.substring(0, fin).toInt();
  int inicio = fin + 1;

  if (codigo == 3) { // Alarma sensor DHT
    stateAlarma = HIGH;
    digitalWrite(alarma, stateAlarma);
    AlarmaSonora();
  }

  else if (codigo == 1) { //1: Parar comunicacio
    Comunicacio = false;
  }

  else if (codigo == 2) { //2: Reanudar comunicacio
    Comunicacio = true;
    NextMillisTIMEOUT = millis() + PeriodeTIMEOUT;

  }

  else if (codigo == 8) { //8: Joystick manual
    MANUAL = true;
  }
  else if (codigo == 7) { //7: Moviment AUTO del servo
    MANUAL = false;
  }
    
  else{
    stateAlarma = LOW;
    digitalWrite(alarma, stateAlarma);
  }
}

void AlarmaSonora() {
  tone(buzzer, 3000, 2000);
}

int LlegirJoystick() {
  int valorJoy = analogRead(joyX);
  int angle = map(valorJoy, 0, 1023, 0, 180);
  return angle;
}

void EnviarJoystick() {
  int angle = LlegirJoystick();
  String missatge = AfegirChecksum("8:" + String(angle)); // ComandoT_ServoJoy = 8
  mySerial.println(missatge);
  Serial.print("Envio Joystick: "); 
  Serial.println(missatge);
}
//--------------------------------------------------
// Programa prinicipal
//--------------------------------------------------

void loop() {
  if (mySerial.available()) {//Sat para python
    digitalWrite(led, HIGH);
    NextMillisTIMEOUT = millis() + PeriodeTIMEOUT;
    digitalWrite(alarma, LOW);

    String comando = mySerial.readStringUntil('\n'); //Rebre
    Serial.println(comando); //Enviar
      
    ProcessarCom(comando);//
    digitalWrite(led, LOW);
  }
  else{
    if (Comunicacio == true && millis()>= NextMillisTIMEOUT){
      Serial.println("4:");
      digitalWrite(alarma, HIGH);
    }
  }

  if(Serial.available()){
    //Python para sat
    String info = Serial.readStringUntil('\n');
    ProcessarCom(info);
    mySerial.println(info);
    Serial.print("Envio:");
    Serial.println(info);
  }
  
  if (MANUAL == true && millis() >= NextMillisJoystick) { //Envia valor de Joystick manual
    NextMillisJoystick = millis() + PeriodeJoystick;
    EnviarJoystick();
  }
}
