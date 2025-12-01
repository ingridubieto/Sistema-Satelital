# Sistema Satel·lital

Projecte de l'assignatura de Ciències de la Computació. Implementació del prototip d'un sistema satel·lital compost pel satèl·lit i l'estació de terra.

### Vídeo de la [Versió 1](https://youtu.be/uBuVtdbzSjU)  
(Que s'aconsegueix fer a la versió 1)

### Vídeo de la [Versió 2](https://youtu.be/e1XV5jPOSLc)  
(Que s'aconsegueix fer a la versió 2)

### Vídeo de la [Versió 3]()  
(Que s'aconsegueix fer a la versió 3)

### Vídeo de la [Versió 4]()  
(Que s'aconsegueix fer a la versió 4)

 _**Estat del projecte:** Versió 3_

## Explicació del **Protocol d'Aplicació** del sistema satel·lital:

### Missatges que envia l'interfície de l'estació de terra al satèl·lit;
  
_**Parar la Transmissió**_ de dades --> 1:
    
_**Reanudar la Transmissió**_ de dades --> 2:
    
_**Periodicitat**_ de les dades enviades --> 3:P  
· On P és el període d'enviament de les dades
    
_**Mode constant**_ de gir del sensor de distància --> 4:  
El servor motor recòrre des de l'àngle 0 al 180, simulant el moviment d'un radar

_**Mode manual**_ de gir del sensor de distància --> 5:A   
El servo motor es dirigeix a la posició desitjada per observar la distància en aquest àngle  
· On A és l'àngle introduit per l'usuari

Placa on es fa el _**Càlcul de les mitjanes;**_  
L'usuari pot triar on fer el càlcul de les mitjanes  
· Si es fa el càlcul des del mateix **satèl·lit** --> 6:0  
· Si es fa el càlcul des de **Python** --> 6:1
  
Definició d'un _**Valor màxim de temperatura**_ --> 7:T'  
· On T' és el valor llindar que fa que salti l'alarma d'alta temperatura

Definició d'un _**Valor màxim de distància**_ --> 8:D'  
· On D' és el valor llindar que fa que salti l'alarma de perill de xoc del satèl·lit amb un objecte

### Missatges destinats a l'interfície de l'estació de terra;

_**Enviament de dades de Temperatura i Humitat**_  --> 1:T:H  
· On T és la temperatura que obté el sensor DHT  
· On H és l'humitat que obté el sensor DHT

_**Enviament de dades de Distància i Àngle**_ --> 2:D:A  
· On D és la distància que obté el sensor d'ultrasons  
· On A és l'angle en el que es troba el servo motor

_**ERROR dades DHT**_ --> 3:  
En el cas que el sensor DHT obtingui un valor NaN de temperatures o humitats, salta una alarma

_**ERROR de comunicació entre arduinos**_ --> 4:  
En el cas que la comunicació via cable o kit LoRa falli, és a dir, que l'estació de terra no rebi ningún missatge del satèl·lit, salta una alarma

_**ERROR de temperatura alta**_ --> 5:  
En el cas que el sensor DHT obtingui un valor superior al llindar de temperatura establert per l'usuari, salta una alarma

_**ERROR de radar**_ --> 6:  
En el cas que el sensor d'ultrasons rebi un valor de distància NaN, salta una alarma

_**ERROR de perill de xoc**_ --> 7:  
En el cas que el sensor d'ultrasons rebi un valor menor al llindar de distància establert per l'usuari, salta una alarma. També voldrà dir que el satèl·lit esta en perill de col·lisió  


(INSERTAR FOTO DE GRUP 11)
![IMATGE DE GRUP 11](assets/nomdelaimatge)
