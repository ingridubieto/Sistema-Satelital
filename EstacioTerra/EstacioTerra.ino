#include <SoftwareSerial.h>

int ComandoT_Parar = 1;
int ComandoT_Reanudar = 2;
int ComandoT_Periode_TyHyD = 3;
int ComandoT_Periode_Pos = 4;
int ComandoT_MitjanesSat = 5;
int ComandoT_MaxTemp = 6;
int ComandoT_MaxHum = 7;
int ComandoT_ServoAuto = 8;
int ComandoT_ServoJoy = 9;
int ComandoT_ServoManual = 10;
int ComandoT_MaxDist = 11;

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

int Checksum(String missatge){
  const char* paraula = missatge.c_str();
  int suma = 0;
  for (int i = 0; paraula[i] != '\0'; i++){
      suma += paraula[i];
  }
  return suma % 256;
}

String AfegirChecksum(String paraula){
  return paraula + "|" + String(Checksum(paraula));
}

void ProcessarCom(String comando) {
  comando.trim();
  int fin = comando.indexOf(':', 0);
  int codigo = comando.substring(0, fin).toInt();
  int inicio = fin + 1;

  if (codigo == ComandoT_Parar) { //1: Parar comunicacio
    Comunicacio = false;
  }

  else if (codigo == ComandoT_Reanudar) { //2: Reanudar comunicacio
    Comunicacio = true;
    NextMillisTIMEOUT = millis() + PeriodeTIMEOUT;

  }
  else if (codigo == ComandoT_ServoJoy) { //9: Joystick manual
    MANUAL = true;
  }
  else if (codigo == ComandoT_ServoAuto) { //8: Moviment AUTO del servo
    MANUAL = false;
  }
  else if (codigo == ComandoT_ServoManual){ // 10 Moviment concret
    MANUAL = false;
  }
}

void AlarmaSonora() {
  digitalWrite(buzzer, HIGH);
  //tone(buzzer, 3000, 2000);
}

int LlegirJoystick() {
  int valorJoy = analogRead(joyX);
  int angle = map(valorJoy, 0, 1023, 0, 180);
  return angle;
}

void EnviarJoystick() {
  int angle = LlegirJoystick();
  String missatge = AfegirChecksum("9:" + String(angle)); // ComandoT_ServoJoy = 8
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
    digitalWrite(buzzer, LOW);

    String comando = mySerial.readStringUntil('\n'); //Rebre
    Serial.println(comando); //Enviar

    digitalWrite(led, LOW);
  }
  else{
    if (Comunicacio == true && millis()>= NextMillisTIMEOUT){
      Serial.println("4:");
      digitalWrite(alarma, HIGH);
      digitalWrite(buzzer, HIGH);
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
