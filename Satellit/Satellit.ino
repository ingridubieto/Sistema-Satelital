#include <SoftwareSerial.h>
#include <DHT.h>
#include <Servo.h>
#include <NewPing.h>
//--------------------------------------
//Definició del protocol d'aplicació: 
//--------------------------------------

//Dades enviades (Sat a Python)

String Comando_TyH = "1:";
String Comando_mTymH = "2:";
String Comando_DyA = "3:";
String Comando_txyz = "4:";
String Comando_ErrorCom = "5:";
String Comando_ErrorDHT = "6:";
String Comando_ErrorTempAlta = "7:";
String Comando_ErrorHumAlta = "8:";
String Comando_ErrorRadar = "9:";
String Comando_ErrorXoc = "10:";
String Comando_Fotos = "11:";

//Dades rebudes (Python i Terra a Sat)

int ComandoT_Parar = 1;
int ComandoT_Reanudar = 2;
int ComandoT_Period = 3;
int ComandoT_MitjanesSat = 4;
int ComandoT_MaxTemp = 5;
int ComandoT_MaxHum = 6;
int ComandoT_ServoAuto = 7;
int ComandoT_ServoJoy = 8;
int ComandoT_ServoManual = 9;
int ComandoT_MaxDist = 10;

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

int PeriodeProva = -10;
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
//Alarma temp alta
float TEMP_LIMIT = 50.0; // llindar de temperatura  inicial, pot ser canviat
int cont_TEMP_LIMIT = 0; // comptador de superacions consecutives del llindar de temperatura
//Alarma Hum alta
float HUM_LIMIT = 80.0;
int cont_HUM_LIMIT = 0;
//El limit consecutiu el reutilitzem pels dos
const int LIMIT_CONSECUTIU = 3; // nombre de cops consecutius que ha de superar el llindar per enviar una alarma

// Inicialització del sensor ultrasons
NewPing sonar(UltrasonicPin, UltrasonicPin, MaxDistance);

// Variables pel càlcul de mitjanes
#define WINDOW 10
int Mitjanes;

// Mitjana Temperatura
double bufferT[WINDOW] = {0};
double sumaT = 0.0;
int indexT = 0;
int countT = 0;
float Mitjana_Temperatura;

// Mitjana Humitat
double bufferH[WINDOW] = {0};
double sumaH = 0.0;
int indexH = 0;
int countH = 0;
float Mitjana_Humitat;

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
    int pos = comando.indexOf('|', 0); //Index de la posició de la barra
    comando = comando.substring(0,pos);

    int fin = comando.indexOf(':', 0);
    int codigo = comando.substring(0, fin).toInt();
    int inicio = fin + 1;

    if (codigo == ComandoT_Parar) { // Parar emissió de dades
      Dades_TyH = false;
      Dades_DyA = false;
    }
    else if (codigo == ComandoT_Reanudar) { // Reanudar emissió de dades
      Dades_TyH = true;
      Dades_DyA = true;
    }
    else if (codigo == ComandoT_Period) { // Canviar periodicitat de dades 
      PeriodeDHT = comando.substring(inicio, pos).toInt(); // extrae el valor del periodo de datos
      PeriodeRADAR = comando.substring(inicio, pos).toInt(); // extrae el valor del periodo de datos
    }
    else if (codigo == ComandoT_MitjanesSat) {
      Mitjanes_T = true; 
    }
    else if (codigo == ComandoT_MaxTemp) {
      TEMP_LIMIT = comando.substring(inicio, pos).toInt(); // Nou límit de temperatura
    }
    else if (codigo == ComandoT_MaxHum) {
      HUM_LIMIT = comando.substring(inicio, pos).toInt(); // Nou límit d'humitat
    }

    else if (codigo == ComandoT_ServoAuto) { // Activar Mode Automàtic del servo
      AUTO = true;
    }
    else if (codigo == ComandoT_ServoJoy) { // Activar Mode Joystick del servo

    }
    else if (codigo == ComandoT_ServoManual) { // Mode manual del servo
      AUTO = false;
      A = comando.substring(inicio, pos).toInt(); // Nova posició del servo
      myservo.write(A);
    }
  }
}

void Enviar_TyH (){
  float H = dht.readHumidity(); // Valor humitat (%)
  float T = dht.readTemperature(); // Valor temperatura (ºC)

  if (isnan(H) || isnan(T)) {
    // Error en la lectura del sensor DHT11
    String missatge = AfegirChecksum(Comando_ErrorDHT); // Alarma 6 -> Error T/H
    mySerial.println(missatge);
    Serial.println(missatge);
  }

  else {
    // Enviament de dades vàlides
    digitalWrite(led, HIGH);
    String missatge = AfegirChecksum(Comando_TyH + String(T) + ":" + String(H)); //Fomrat missatge 1:Temperatura:Humitat|Checksum
    mySerial.println(missatge);
    Serial.println(missatge);
    digitalWrite(led, LOW);
  
    // Control d’alarma en cas d'alta temperatura
    if (T >= TEMP_LIMIT) {
      cont_TEMP_LIMIT++;
      if (cont_TEMP_LIMIT >= LIMIT_CONSECUTIU) {
        String missatge = AfegirChecksum(Comando_ErrorTempAlta); // Alarma 7 -> Alta temperatura
        mySerial.println(missatge);
        Serial.println(missatge);
      }
    }
    else {
      cont_TEMP_LIMIT = 0; // Reiniciem si baixa del límit
    }

    // Control d’alarma en cas d'humitat alta
    if (H >= HUM_LIMIT) {
      cont_HUM_LIMIT++;
      if (cont_HUM_LIMIT >= LIMIT_CONSECUTIU) {
        String missatge = AfegirChecksum(Comando_ErrorHumAlta); // Alarma 8 -> HUmitat temperatura
        mySerial.println(missatge);
        Serial.println(missatge);
      }
    }
    else {
      cont_HUM_LIMIT = 0; // Reiniciem si baixa del límit
    }
    
  }

}

double actualitzar_Mitjana(double nou_valor, double buffer[], double &suma, int &indexPos, int &contador){
  suma -= buffer[indexPos];
  buffer[indexPos] = nou_valor;
  suma += nou_valor;

  indexPos = (indexPos + 1) % WINDOW; //Mira la següent posicio circularment amb 10 elements

  if (contador < WINDOW) {
    contador++;
  }
  return suma / contador;
}

void Enviar_mTymH(){
  Mitjana_Temperatura = actualitzar_Mitjana(T, bufferT, sumaT, indexT, countT);
  Mitjana_Humitat = actualitzar_Mitjana(H, bufferH, sumaH, indexH, countH);
  String missatge = AfegirChecksum(Comando_mTymH + String(Mitjana_Temperatura) + ":" + String(Mitjana_Humitat)); //Format missatge 2:Mitjana_Temperatura:Mitjana_Humitat|Checksum
  mySerial.println(missatge);
  Serial.println(missatge);
}

void Enviar_DyA (){ //Comando 3:D:A //Error radar 9:
  float D = sonar.ping_cm(); // Valor distància (cm)

  if (D <= 0 || isnan(D)) {
    // Error en la lectura de l'ultrasons
    String missatge = AfegirChecksum(Comando_ErrorRadar); // Alarma 6 -> Error Radar D/A
    mySerial.println(missatge);
    Serial.println(missatge);
  } 
  else {
    // Enviamnet dades correctes D/A
    digitalWrite(led, HIGH);
    String missatge = AfegirChecksum(Comando_DyA + String(D) + ":" + String(A)); //Format missatge 2:Distancia:Angle|Checksum
    mySerial.println(missatge);
    Serial.println(missatge);
    digitalWrite(led, LOW);
  }
}

void Enviar_txyz (){
  //Comando 4:t:x:y:z dades de posició del satel·lit
  //Comando_txyz
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
    if (Mitjanes == true){
      Enviar_mTymH();
    }
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
