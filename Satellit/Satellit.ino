#include <SoftwareSerial.h>
#include <DHT.h>
#include <Servo.h>

//Definicio led enviament
const int led = 12;  // LED en el pin 12 (Rojo)
bool stateLed = LOW;

//Definició sensor DHT
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//Definició comunicació
SoftwareSerial mySerial(10, 11); // RX, TX

//Definició servo motor
Servo myservo;
int pos = 0; //posició inicial del servo

long nextMillisDHT;
const long intervalDHT = 10000;
const long nextMillinsDHT = 10000; // 10 segundos para el sensor de humedad i temperatura DHT
long nextTimeoutHT = 5000;
unsigned long previousMillis = 0; //??

bool esperandoTimeout = false;
bool AUTO = false; //Mode Automatic del servo comença desconectat

void setup() {
    //Definció leds
    pinMode(led, OUTPUT);

    myservo.attach(9); //Pin del servo
    myservo.write(0); // posición inicial del servo

    Serial.begin(9600);
    dht.begin();

    mySerial.begin(9600);

    // primer instante en el que habrá que cambiar
    nextMillisDHT = millis() + intervalDHT;
}

void loop() {

      float h = dht.readHumidity();
      float t = dht.readTemperature();

    if (isnan(h) || isnan(t)){
      Serial.println("Error al leer el sensor DHT11");
      esperandoTimeout = false;
    }

    else {
      nextTimeoutHT = millis() + 5000; // 5 segundos
      esperandoTimeout = true;
      stateLed = HIGH;
      digitalWrite(led, stateLed);
      mySerial.print(t);
      Serial.print(t);
      mySerial.print(":");
      Serial.print(":");
      mySerial.println(h);
      Serial.println(h);
      stateLed = LOW;
      digitalWrite(led, stateLed);
    } 

    if (!esperandoTimeout && (millis() >= nextTimeoutHT)) {
      mySerial.println ("Fallo");
      Serial.println("Fallo");
    }

    delay(1000);

    if (Serial.available() > 0) { 
      String comando = Serial.readStringUntil('\n');
      comando.trim();
      int fin=comando.indexOf(':',0);
      int codigo = comando.substring(0, fin).toInt();
      int inicio = fin+1;
      if (codigo == 4) { // Modo constante de giro del sensor distancia
        AUTO = true;
      }
      else if (codigo == 5) { // Modo manual de giro del sensor distancia
        AUTO = false;
        fin=comando.indexOf(':',inicio);
        pos = comando.substring(inicio, fin).toInt(); // extrae el valor de la posición
        myservo.write(pos); // el servo se mueve hacia la posición
      }
    }
    if (AUTO) {
      for (pos = 0; pos <= 180; pos += 1) {
        myservo.write(pos);
        delay(15);
      }
      for (pos = 180; pos >= 0; pos -= 1) {
        myservo.write(pos);
        delay(15);
      }
    }
  }