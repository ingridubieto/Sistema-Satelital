#include <SoftwareSerial.h>

// Definició servo motor
int A = 0; // posició del servo en tot moment
int direccioServo = 1; // 1 anant "Endavant" -1 anant "Endarrera"

// Definició sensors i temporitzadors
int Periode = 1000; // periodicitat inicial d’enviament de dades (1 segons), pot ser canviada
int PeriodeSERVO = 15;
int PeriodeMITJANES = 1000;
long NextMillisDHT;
long NextMillisRADAR;
long NextMillisSERVO;
long NextMillisMITJANES;
long NextMillisPOS;
const int MaxDistance = 200; // màxima distància en cm

// Booleans d’estat Declarat a fora les funcions perque siguin globals
bool AUTO = true; // Modo automàtic del servo, comença connectat
bool JOYSTICK = false; // Mode joystick del servo.
bool Mitjanes = false; // On es fa el càlcul de la mitjana.
bool Dades_TyH = true; // Estat emissió dades de T i H, comença connectat
bool Dades_DyA = true; // Estat emissió dades de D i A, comença connectat
bool Dades_Posicio = true; // Estat emissió dades de Posició del satèl·lit, comença connectat

// Control d’alarmes 
float TEMP_LIMIT = 50.0; // llindar de temperatura  inicial, pot ser canviat
float HUM_LIMIT = 100.0; // llindar d'humitat inicial, pot ser canviat
float DIST_LIMIT = 60.0; // llindar de distància inicial, pot ser canviat
int cont_TEMP_LIMIT = 0; // comptador de superacions consecutives del llindar de temperatura
int cont_HUM_LIMIT = 0; // comptador de superacions consecutives del llindar d'humitat
const int LIMIT_CONSECUTIU_TEMP = 3; // nombre de cops consecutius que ha de superar el llindar de temperatura per enviar una alarma
const int LIMIT_CONSECUTIU_HUM = 3; // nombre de cops consecutius que ha de superar el llindar d'humitat per enviar una alarma

float H; // Valor humitat (%)
float T; // Valor temperatura (ºC)

// Constants
const double G = 6.67430e-11;  // Gravitational constant (m^3 kg^-1 s^-2)
const double M = 5.97219e24;   // Mass of Earth (kg)
const double R_EARTH = 6371000;  // Radius of Earth (meters)
const double ALTITUDE = 400000;  // Altitude of satellite above Earth's surface (meters)
const double EARTH_ROTATION_RATE = 7.2921159e-5;  // Earth's rotational rate (radians/second)
const unsigned long MILLIS_BETWEEN_UPDATES = 1000; // Time in milliseconds between each orbit simulation update
const double  TIME_COMPRESSION = 90.0; // Time compression factor (90x)

// Variables
unsigned long nextUpdate; // Time in milliseconds when the next orbit simulation update should occur
double real_orbital_period;  // Real orbital period of the satellite (seconds)
double r;  // Total distance from Earth's center to satellite (meters)

void setup() {
  Serial.begin(9600);

  // Inicialització temporitzadors
  NextMillisDHT = millis();
  NextMillisRADAR = millis();
  NextMillisSERVO = millis();
  NextMillisMITJANES = millis();
  NextMillisPOS = millis();

  nextUpdate = MILLIS_BETWEEN_UPDATES;
    
  r = R_EARTH + ALTITUDE;
  real_orbital_period = 2 * PI * sqrt(pow(r, 3) / (G * M));
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
      Dades_Posicio = false;
    }
    else if (codigo == 2) { // Reanudar emissió de dades
      Dades_TyH = true;
      Dades_DyA = true;
      Dades_Posicio = true;
    }
    else if (codigo == 3) { // Canviar periodicitat de dades 
      Periode = comando.substring(inicio, fin).toInt(); // extrae el valor del periodo de datos
    }
    else if (codigo == 4) { // Mitjanes de Temperatura i Humitat
      Mitjanes = true;
    }
    else if (codigo == 5) { // Nou límit de temperatura llindar
      TEMP_LIMIT = comando.substring(inicio, fin).toInt();
    }
    else if (codigo == 6) { // Nou límit d'humitat llindar
      HUM_LIMIT = comando.substring(inicio, fin).toInt();
    }
    else if (codigo == 7) { // Mode Constant/Automàtic de gir
      AUTO = true;
      JOYSTICK = false;
    }
    else if (codigo == 8) { // Mode JoyStick manual de gir
      AUTO = false;
      JOYSTICK = true;
    }
    else if (codigo == 9) { // Mode manual de gir
      AUTO = false;
      JOYSTICK = false;
      A = comando.substring(inicio, fin).toInt();
    }
    else if (codigo == 10) { //Nou límit de distància llindar
      DIST_LIMIT = comando.substring(inicio, fin).toInt();
    }
  } 
}

void Enviar_TyH (){
  float H = random(40, 80); // Valor humitat (%)
  float T = random(15, 30); // Valor temperatura (ºC)

  // Enviament de dades vàlides
  String missatge = AfegirChecksum("1:" + String(T) + ":" + String(H)); //Format missatge 1:Temperatura:Humitat|Checksum
  Serial.println(missatge);

  if(Mitjanes){
    float Temp_Mitjana = random(15, 30);
    float Hum_Mitjana = random(40, 80);
    String missatge = AfegirChecksum("2:" + String(Temp_Mitjana) + ":" + String(Hum_Mitjana)); //Format missatge 2:Mitjana_Temperatura:Mitjana_Humitat|Checksum
    Serial.println(missatge);
  }
  
  // Control d’alarma en cas d'alta temperatura
  if (T >= TEMP_LIMIT) {
    cont_TEMP_LIMIT++;
    if (cont_TEMP_LIMIT >= LIMIT_CONSECUTIU_TEMP) {
      String missatge = AfegirChecksum("7:"); // Alarma 7: --> Alta temperatura
      Serial.println(missatge);
    }
  } 
  else {
    cont_TEMP_LIMIT = 0; // Reiniciem si baixa del límit
  }

  // Control d’alarma en cas d'alta humitat
  if (H >= HUM_LIMIT) {
    cont_HUM_LIMIT++;
    if (cont_HUM_LIMIT >= LIMIT_CONSECUTIU_HUM) {
      String missatge = AfegirChecksum("8:"); // Alarma 8: --> Alta humitat
      Serial.println(missatge);
    }
  } 
  else {
    cont_HUM_LIMIT = 0; // Reiniciem si baixa del límit
  }
}

void Enviar_DyA (){
  float D = random(0, 50); // Valor distància (cm)

  // Enviamnet dades correctes D/A
  String missatge = AfegirChecksum("3:" + String(D) + ":" + String(A)); //Format missatge 3:Distancia:Angle|Checksum
  Serial.println(missatge);

  // Control d’alarma en cas de perill de xoc
  if (D >= DIST_LIMIT) {
    String missatge = AfegirChecksum("10:"); // Alarma 10: --> Perill de xoc
    Serial.println(missatge);
  }
}

void MoureServo (){
  if (AUTO == true){
    A = random(0, 180);
  }
}

void Enviar_Posicio (unsigned long millis, double inclination, int ecef){
  double time = (millis / 1000) * TIME_COMPRESSION;  // Real orbital time
    double angle = 2 * PI * (time / real_orbital_period);  // Angle in radians
    double x = r * cos(angle);  // X-coordinate (meters)
    double y = r * sin(angle) * cos(inclination);  // Y-coordinate (meters)
    double z = r * sin(angle) * sin(inclination);  // Z-coordinate (meters)

    if (ecef) {
        double theta = EARTH_ROTATION_RATE * time;
        double x_ecef = x * cos(theta) - y * sin(theta);
        double y_ecef = x * sin(theta) + y * cos(theta);
        x = x_ecef;
        y = y_ecef;
    }
  String missatge = AfegirChecksum("4:" + String(time) + ":" + String(x) + ":" + String(y) + ":" + String(z)); //Format missatge 4:temps:x:y:z|Checksum
}

//--------------------------------------------------
// Programa prinicipal
//--------------------------------------------------

void loop() {
  if (Serial.available()){
    String comando = Serial.readStringUntil('\n');
    ProcessarCom(comando);
  }

  if ((Dades_TyH == true) && (millis() >= NextMillisDHT)){
    NextMillisDHT = millis() + Periode;
    Enviar_TyH();
  }

  if ((Dades_DyA == true) && (millis() >= NextMillisRADAR)){
    NextMillisRADAR = millis() + Periode;
    Enviar_DyA();
  }

  if (millis() >= NextMillisSERVO) {
    NextMillisSERVO = millis() + PeriodeSERVO;
    MoureServo();
  }

  if ((Dades_Posicio == true) && (millis() >= NextMillisPOS)){
    NextMillisPOS = millis() + Periode;
    Enviar_Posicio(millis(), 0.0, 1);
  }
  unsigned long currentTime = millis();
    if(currentTime>nextUpdate) {
        Enviar_Posicio(currentTime, 0.0, 1);
        nextUpdate = currentTime + MILLIS_BETWEEN_UPDATES;
    }
}

Em marca malament dins del loop: Enviar_Posicio(); i simulate_orbit(currentTime, 0, 0);