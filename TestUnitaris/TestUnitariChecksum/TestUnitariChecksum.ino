#include <SoftwareSerial.h>

void setup() {
  Serial.begin(9600);
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

//--------------------------------------------------
// Programa prinicipal
//--------------------------------------------------

void loop() {
  String paraula = "Miau";
  int resultat = Checksum(paraula);
  Serial.println(resultat);
  String missatge = AfegirChecksum(paraula);
  Serial.println(missatge);
  CompararChecksum(missatge);
  delay(1000);
}
