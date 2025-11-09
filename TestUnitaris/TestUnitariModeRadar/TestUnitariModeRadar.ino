#include <SoftwareSerial.h>
#include <Servo.h>

SoftwareSerial mySerial(10, 11);
Servo myservo;
bool AUTO = false;
unsigned long previousMillis = 0;
int pos = 0;

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  myservo.attach(9); // pin del servo 9
  myservo.write(0); // posición inicial del servo
}

void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();

    int fin=comando.indexOf(':',0);
    int codigo = comando.substring(0, fin).toInt(); 
    int inicio = fin+1;

    if (codigo == 4){ // Modo constante de giro del sensor distancia
      AUTO = true;
    }
    else if (codigo == 5){ // Modo manual de giro del sensor distancia
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