#include <SoftwareSerial.h>
#include <DHT.h>
#include <Servo.h>
#include <NewPing.h>

// Definició LED enviament
const int led = 12;  // LED en el pin 12 (Verda)
bool stateLed = LOW;

// Definició sensor DHT
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Definició comunicació
SoftwareSerial mySerial(10, 11); // RX, TX

// Definició servo motor
Servo myservo;
int A = 0; // posició del servo en tot moment
int direccioServo = 1; // 1 anant "Endavant" -1 anant "Endarrera"

// Definició sensors i temporitzadors
int PeriodeDHT = 1000; // periodicitat inicial d’enviament de dades (1 segons), pot ser canviada
int PeriodeRADAR = 1000;
int PeriodeSERVO = 15;
int PeriodeMITJANES = 1000;
long NextMillisDHT;
long NextMillisRADAR;
long NextMillisSERVO;
long NextMillisMITJANES;
const int UltrasonicPin = 5; // pin del sensor ultrasons
const int MaxDistance = 200; // màxima distància en cm

// Booleans d’estat Declarat a fora les funcions perque siguin globals
bool AUTO = true; // Modo automàtic del servo, comença connectat
<<<<<<< HEAD
bool Dades_TyH = false; // Estat emissió dades de T i H, comença desconnectat
bool Dades_DyA = false; // Estat emissió dades de D i A, comença desconectat
bool Mitjanes_T = false; // On es fa el càlcul de la mitjana.
=======
bool Dades_TyH = true; // Estat emissió dades de T i H, comença desconnectat
bool Dades_DyA = true; // Estat emissió dades de D i A, comença desconectat
>>>>>>> 2ef52181992715da1912a1e5111921867cd3ff12

// Control d’alarmes 
const float TEMP_LIMIT = 30.0; // llindar de temperatura  inicial, pot ser canviat
int cont_TEMP_LIMIT = 0; // comptador de superacions consecutives del llindar de temperatura
const int LIMIT_CONSECUTIU = 3; // nombre de cops consecutius que ha de superar el llindar per enviar una alarma

// Inicialització del sensor ultrasons
NewPing sonar(UltrasonicPin, UltrasonicPin, MaxDistance);

// Variables pel càlcul de mitjanes de T
float suma_T = 0;
float Mitja = 0;
int Ts = 0;

void setup() {
// Definició LED
  pinMode(led, OUTPUT);

  // Definició servo motor
  myservo.attach(9); // Pin del servo
  myservo.write(0);  // Posició inicial

  Serial.begin(9600);
  mySerial.begin(9600);
  dht.begin();

  // Inicialització temporitzadors
  NextMillisDHT = millis();
  NextMillisRADAR = millis();
  NextMillisSERVO = millis();
  NextMillisMITJANES = millis();
}

//--------------------------------------------------
// Definició de les funcions
//--------------------------------------------------

void ProcessarCom(String comando) {
    comando.trim();
    int fin = comando.indexOf(':', 0);
    int codigo = comando.substring(0, fin).toInt();
    int inicio = fin + 1;
    
    if (codigo == 1) { // Parar emissió de dades
      Dades_TyH = false;
      Dades_DyA = false;
    }
    else if (codigo == 2) { // Reanudar emissió de dades
      Dades_TyH = true;
      Dades_DyA = true;
    }
    else if (codigo == 3) { // Canviar periodicitat de dades 
      PeriodeDHT = comando.substring(inicio, fin).toInt(); // extrae el valor del periodo de datos
    }
    else if (codigo == 4) { // Activar Mode Automàtic del servo
      AUTO = true;
    }
    else if (codigo == 5) { // Mode manual del servo
      AUTO = false;
      A = comando.substring(inicio, fin).toInt(); // Nova posició del servo
      myservo.write(A);
    }
    else if (codigo == 6) { // Mitjanes de temperatura
      if((millis() >= 10000)&&(millis() >= NextMillisMITJANES)){
        Enviar_Mitjanes();
      }
    }
    else if (codigo == 6) {
      M = comando.substring(inicio, fin).toInt();
      if (M == 0) { // El càlcul de les mitjanes de T es fa des del satèl·lit
        Mitjanes_T = true; 
      }
    }
    else if (codigo == 7) {
      TEMP_LIMIT = comando.substring(inicio, fin).toInt(); // Nou límit de temperatura
    }
}

void Enviar_TyH (){
  float H = dht.readHumidity(); // Valor humitat (%)
  float T = dht.readTemperature(); // Valor temperatura (ºC)

  if (isnan(H) || isnan(T)) {
    // Error en la lectura del sensor DHT11
    mySerial.println("3:"); // Alarma 3 -> Error T/H
    Serial.print("Error");
  }

  else {
    // Enviament de dades vàlides
    digitalWrite(led, HIGH);
    mySerial.print(1); // Identificador emissió T/H
    mySerial.print(":");
    mySerial.print(T); // Temperatura
    mySerial.print(":");
    mySerial.println(H); // Humitat
    digitalWrite(led, LOW);
    Serial.print(1); // Identificador emissió T/H
    Serial.print(":");
    Serial.print(T); // Temperatura
    Serial.print(":");
    Serial.println(H); // Humitat
  
    // Control d’alarma en cas d'alta temperatura
    if (T >= TEMP_LIMIT) {
      cont_TEMP_LIMIT++;
      if (cont_TEMP_LIMIT >= LIMIT_CONSECUTIU) {
        mySerial.println("5:"); // Alarma 5 -> Alta temperatura
      }
    } 
    else {
      cont_TEMP_LIMIT = 0; // Reiniciem si baixa del límit
    }
  }

}

void Enviar_DyA (){
  float D = sonar.ping_cm(); // Valor distància (cm)

  if (D <= 0 || isnan(D)) {
    // Error en la lectura de l'ultrasons
    mySerial.println("6:"); // Alarma 6 -> Error D/A
  } 
  else {
    digitalWrite(led, HIGH);
    mySerial.print(2); // Identificador emissió D/A
    mySerial.print(":");
    mySerial.print(D); // Distància
    mySerial.print(":");
    mySerial.println(A); // Angle
    digitalWrite(led, LOW);
  }
}

void Enviar_Mitjanes(){

}

void MoureServo (){
  if (AUTO == true){
    A = A + direccioServo;

    if (A >= 180){
      A = 180;
      direccioServo = -1;
    }
    else if (A <= 0){
      A = 0;
      direccioServo = 1;
    }
    myservo.write(A);
  }

  else { // Mode manual, definir A
    myservo.write(A);
  }
}

void CalcularMitjanes (){
  while (Ts<=10){
    suma_T = suma_T + T;
    Mitja = suma_T / 10;
    mySerial.println(Mitja);
    Ts = Ts+1;
  }
}

//--------------------------------------------------
// Programa prinicipal
//--------------------------------------------------

void loop() {
  if (Serial.available()){
    String comando = Serial.readStringUntil('\n');
    ProcessarCom(comando);
    Serial.println("Available");
  }

  if ((Dades_TyH == true) && (millis() >= NextMillisDHT)){
    NextMillisDHT = millis() + PeriodeDHT;
    Enviar_TyH();
    Serial.println("DHT");
  }

  if ((Dades_DyA == true) && (millis() >= NextMillisRADAR)){
    NextMillisRADAR = millis() + PeriodeRADAR;
    Enviar_DyA();
    Serial.println("Radar");

  }

  if (millis() >= NextMillisSERVO) {
    NextMillisSERVO = millis() + PeriodeSERVO;
    MoureServo();

  }

  if ((Mitjanes_T == true) {
    CalcularMitjanes ();
  }
}
