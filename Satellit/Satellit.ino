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
const int ServoPin = 9; // Pin del servo

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
bool Mitjanes_T = false; // On es fa el càlcul de la mitjana.

bool Dades_TyH = true; // Estat emissió dades de T i H, comença connectat
bool Dades_DyA = true; // Estat emissió dades de D i A, comença connectat

// Control d’alarmes 
float TEMP_LIMIT = 50.0; // llindar de temperatura  inicial, pot ser canviat
int cont_TEMP_LIMIT = 0; // comptador de superacions consecutives del llindar de temperatura
const int LIMIT_CONSECUTIU = 3; // nombre de cops consecutius que ha de superar el llindar per enviar una alarma

// Inicialització del sensor ultrasons
NewPing sonar(UltrasonicPin, UltrasonicPin, MaxDistance);

// Variables pel càlcul de mitjanes de T
#define WINDOW 10
double buffer[WINDOW] = {0};
int Longitud_buffer = 0;
float Temp_Mitjana = 0;
int Index_Mitjana_Temp = 0;
float Suma_Temp = 0;

int M;

float H; // Valor humitat (%)
float T; // Valor temperatura (ºC)

void setup() {
// Definició LED
  pinMode(led, OUTPUT);

  // Definició servo motor
  myservo.attach(ServoPin); // Pin del servo
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

int Checksum(String missatge){
  const char* paraula = missatge.c_str();
  int suma = 0;
  for (int i = 0; paraula[i] != '\0'; i++){
      suma = suma + paraula[i];
  }
  int resultat = suma % 256;
  return resultat;

}

bool CompararChecksum(String missatge){
  missatge.trim();
  int pos = missatge.indexOf('|', 0); //Index de la posició de la barra
  int ChecksumEnviat = missatge.substring(pos + 1).toInt();
  String paraula = missatge.substring(0, pos);
  if (ChecksumEnviat == Checksum(paraula)){
    Serial.println("Bo");
    return true;
  }
  else{
    Serial.println("Missatge per descartar");
    return false;
  }
}

String AfegirChecksum(String paraula){
  String missatge = paraula + "|" + String(Checksum(paraula));
  return missatge;
}

void ProcessarCom(String comando) {
  Serial.print("Terra:");
  Serial.println(comando);

  if (CompararChecksum(comando) == true){
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
}

void Enviar_TyH (){
  float H = dht.readHumidity(); // Valor humitat (%)
  float T = dht.readTemperature(); // Valor temperatura (ºC)

  if (isnan(H) || isnan(T)) {
    // Error en la lectura del sensor DHT11
    String missatge = AfegirChecksum("3:"); // Alarma 3 -> Error T/H
    mySerial.println(missatge);
    Serial.println(missatge);
  }

  else {
    // Enviament de dades vàlides
    digitalWrite(led, HIGH);
    String missatge = AfegirChecksum("1:" + String(T) + ":" + String(H)); //Fomrat missatge 1:Temperatura:Humitat|Checksum
    mySerial.println(missatge);
    Serial.println(missatge);
    digitalWrite(led, LOW);

    if(Mitjanes_T){
      Suma_Temp = Suma_Temp - buffer[Index_Mitjana_Temp]; //Restar la temperatura que hi havia en X posicio
      buffer[Index_Mitjana_Temp] = T; //Insertar la nova temperatura
      Suma_Temp = Suma_Temp + T; //Sumar la nova temperatura
      Index_Mitjana_Temp = (Index_Mitjana_Temp + 1) % WINDOW; //Avançar la posicio

      if (Longitud_buffer < WINDOW){
        Longitud_buffer++;
      }

      if (Longitud_buffer == WINDOW){
        Temp_Mitjana = Suma_Temp / Longitud_buffer; //Calcul mitjana
        String missatge = AfegirChecksum("10:" + String(Temp_Mitjana));
        mySerial.println(missatge);
        Serial.println(missatge);
      }
    }
  
    // Control d’alarma en cas d'alta temperatura
    if (T >= TEMP_LIMIT) {
      cont_TEMP_LIMIT++;
      if (cont_TEMP_LIMIT >= LIMIT_CONSECUTIU) {
        String missatge = AfegirChecksum("5:"); // Alarma 5 -> Alta temperatura
        mySerial.println(missatge);
        Serial.println(missatge);
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
    String missatge = AfegirChecksum("6:"); // Alarma 6 -> Error D/A
    mySerial.println(missatge);
    Serial.println(missatge);
  } 
  else {
    // Enviamnet dades correctes D/A
    digitalWrite(led, HIGH);
    String missatge = AfegirChecksum("2:" + String(D) + ":" + String(A)); //Format missatge 2:Distancia:Angle|Checksum
    mySerial.println(missatge);
    Serial.println(missatge);
    digitalWrite(led, LOW);
  }
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

//--------------------------------------------------
// Programa prinicipal
//--------------------------------------------------

void loop() {
  if (mySerial.available()){
    String comando = mySerial.readStringUntil('\n');
    ProcessarCom(comando);
    //Serial.println("Available");
  }

  if ((Dades_TyH == true) && (millis() >= NextMillisDHT)){
    NextMillisDHT = millis() + PeriodeDHT;
    Enviar_TyH();
    //Serial.println("DHT");
  }

  if ((Dades_DyA == true) && (millis() >= NextMillisRADAR)){
    NextMillisRADAR = millis() + PeriodeRADAR;
    Enviar_DyA();
    //Serial.println("Radar");

  }

  if (millis() >= NextMillisSERVO) {
    NextMillisSERVO = millis() + PeriodeSERVO;
    MoureServo();
    //Serial.println("Servo");

  }
}
