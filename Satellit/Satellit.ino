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

// Definició sensors i temporitzadors
int periodo = 5000; // periodicitat inicial d’enviament de dades (5 segons), pot ser canviada
long nextMillisDHT;
long nextMillisSENSOR;
const int UltrasonicPin = 5; // pin del sensor ultrasons
const int MaxDistance = 200; // màxima distància en cm

// Booleans d’estat
bool AUTO = false; // Modo automàtic del servo, comença desconnectat
bool DADES_TyH = false; // Estat emissió dades de T i H, comença desconnectat
bool DADES_DyA = false; // Estat emissió dades de D i A, comença desconectat

// Control d’alarmes 
const float TEMP_LIMIT = 30.0; // llindar de temperatura  inicial, pot ser canviat
int cont_TEMP_LIMIT = 0; // comptador de superacions consecutives del llindar de temperatura
const int LIMIT_CONSECUTIU = 3; // nombre de cops consecutius que ha de superar el llindar per enviar una alarma

// Inicialització del sensor ultrasons
NewPing sonar(UltrasonicPin, UltrasonicPin, MaxDistance);

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
  nextMillisDHT = millis();
  nextMillisSENSOR = millis();
}

void loop() {
  float H = dht.readHumidity(); // Valor humitat (%)
  float T = dht.readTemperature(); // Valor temperatura (ºC)
  float D = sonar.ping_cm(); // Valor distància (cm)

// LECTURA DE LES PETICIONS DE L'ESTACIÓ DE TERRA //
  if (Serial.available() > 0) { 
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    int fin = comando.indexOf(':', 0);
    int codigo = comando.substring(0, fin).toInt();
    int inicio = fin + 1;
    
    if (codigo == 1) { // Parar emissió de dades
      DATOS_TyH = false;
      DATOS_DyA = false;
    }
    else if (codigo == 2) { // Reanudar emissió de dades
      DATOS_TyH = true;
      DATOS_DyA = true;
    }
    else if (codigo == 3) { // Canviar periodicitat de dades 
      periodo = comando.substring(inicio, fin).toInt(); // extrae el valor del periodo de datos
    }
    else if (codigo == 4) { // Activar Mode Automàtic del servo
      AUTO = true;
    }
    else if (codigo == 5) { // Mode manual del servo
      AUTO = false;
      A = comando.substring(inicio, fin).toInt(); // Nova posició del servo
      myservo.write(A);
    }
  }

  // LECTURA I ENVIAMENT TEMPERATURA I HUMITAT //
  if (DATOS_TyH && millis() - nextMillisDHT >= periodo) {
    nextMillisDHT = millis();

    float H = dht.readHumidity(); // Humitat en %
    float T = dht.readTemperature(); // Temperatura en ºC

    if (isnan(H) || isnan(T)) {
      // Error en la lectura del sensor DHT11
      mySerial.println("3:"); // Alarma 3 -> Error T/H
      cont_TEMP_LIMIT = 0;   // Reiniciem el comptador
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

      // Control d’alarma en cas d'alta temperatura
      if (T >= TEMP_LIMIT) {
        cont_TEMP_LIMIT++;
        if (cont_TEMP_LIMIT >= LIMIT_CONSECUTIVU) {
          mySerial.println("5:"); // Alarma 5 -> Alta temperatura
          cont_TEMP_LIMIT = 0; // Reiniciem comptador
        }
      } 
      else {
        contadorTempAlta = 0; // Reiniciem si baixa del límit
      }
    }
  }
  // LECTURA I ENVIAMENT DISTÀNCIA I ANGLE //
  if (DATOS_DyA && millis() - nextMillisSENSOR >= periodo) {
    nextMillisSENSOR = millis();

    float D = sonar.ping_cm(); // Obté la distància (cm)

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
  // MODE AUTOMÀTIC DEL SERVO MOTOR //
  if (AUTO) {
    for (A = 0; A <= 180; A += 1) {
      myservo.write(A);
      delay(15);
    }
    for (A = 180; A >= 0; A -= 1) {
      myservo.write(A);
      delay(15);
    }
  }
}