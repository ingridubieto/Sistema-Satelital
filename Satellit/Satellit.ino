#include <SoftwareSerial.h>
#include <DHT.h>


//Definicio led enviament
const int led = 12;  // LED en el pin 12 (Rojo)
bool stateLed = LOW;

//Definició sensor DHT
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//Definició comunicació
SoftwareSerial mySerial(10, 11); // RX, TX 

long nextMillisDHT;
const long intervalDHT = 10000;
const long nextMillinsDHT = 10000; // 10 segundos para el sensor de humedad i temperatura DHT
long nextTimeoutHT = 5000;

bool esperandoTimeout = false;

void setup() {
    //Definció leds
    pinMode(led, OUTPUT);


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
}