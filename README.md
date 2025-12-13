# Sistema Satel·lital

Projecte de l'assignatura de Ciències de la Computació. Implementació del prototip d'un sistema satel·lital compost pel satèl·lit i l'estació de terra.

### Vídeo de la [Versió 1](https://youtu.be/uBuVtdbzSjU)  
En la primera versió d'aquest projete es va aconseguir el següent:   
· L'emissió de dades entre els dos arduinos   
· La detecció d'errors en captar les dades del sensor DHT   
· Implementació d'un LED que s'encén cada vegada que l'arduino satèl·lit envia dades vàlides   
· La detecció de un fallo en la comunicació entre els arduinos, és a dir, si s'esta més de 5 segons sense haver-hi intercanvi de dades entre les dues plaques salta una alarma   
· Implementació d'un LED que s'encén cada vegada que l'arduino de l'estació de terra rep dades vàlides   
· Definició de la funció per processar les dades que arriben del satèl·lit   
· Definició de les ordres de iniciar, parar i reanudar les dades que rebem   
· Creació d'una interfície amb botons i una gràfica que recull les dades de temperatura rebudes   

### Vídeo de la [Versió 2](https://youtu.be/e1XV5jPOSLc)  
En la segona versió d'aquest projecte es va aconseguir el següent:
· 

### Vídeo de la [Versió 3](https://youtu.be/HDT-QbDbMX0)  
En la tercera versió d'aquest projecte es va aconseguir el següent:
· 

### Vídeo de la [Versió 4]()  
En la quarta versió d'aquest projecte s'ha aconseguit el següent:
· 

 _**Estat del projecte:** Versió 3_

## Explicació del **Protocol d'Aplicació** del sistema satel·lital:

### Missatges que envia l'interfície de l'estació de terra al satèl·lit;
  
_**Parar la Transmissió**_ de dades --> 1:
    
_**Reanudar la Transmissió**_ de dades --> 2:
    
_**Periodicitat**_ de les dades enviades --> 3:P  
· On P és el període d'enviament de les dades

Placa on es fa el _**Càlcul de les mitjanes;**_  
L'usuari pot triar on fer el càlcul de les mitjanes  
· Si es fa el càlcul des del mateix **satèl·lit** --> 4:0  
· Si es fa el càlcul des de **Python** --> Simplement s'activa una funció definida al python   
Per Parar el càlcul de mitjanes s'envia --> 4:1 (i al mateix temps es deshabilita el càlcul a python)

Definició d'un _**Valor màxim de temperatura**_ --> 5:T'  
· On T' és el valor llindar que fa que salti l'alarma d'alta temperatura

Definició d'un _**Valor màxim d'humitat**_ --> 6:H'  
· On H' és el valor llindar que fa que salti l'alarma d'alta humitat

_**Mode constant**_ de gir del sensor de distància --> 7:  
El servor motor recòrre des de l'àngle 0 al 180, simulant el moviment d'un radar

_**Mode joystick**_ de gir del sensor de distància --> 8:  
El servor motor es mourà a raó del moviment del joystick que faci l'usuari

_**Mode manual**_ de gir del sensor de distància --> 9:A   
El servo motor es dirigeix a la posició desitjada per observar la distància en aquest àngle  
· On A és l'àngle introduit per l'usuari

Definició d'un _**Valor màxim de distància**_ --> 10:D'  
· On D' és el valor llindar que fa que salti l'alarma de perill de xoc del satèl·lit amb un objecte

### Missatges destinats a l'interfície de l'estació de terra;

_**Enviament de dades de Temperatura i Humitat**_  --> 1:T:H  
· On T és la temperatura que obté el sensor DHT  
· On H és l'humitat que obté el sensor DHT

_**Enviament de mitjanes de Temperatura i Humitat**_  --> 2:mT:mH  
· On mT és la mitjana de temperatura de les últimes 10 dades, que calcula el satèl·lit
· On mH és la mitjana d'humitat de les últimes 10 dades, que calcula el satèl·lit

_**Enviament de dades de Distància i Àngle**_ --> 3:D:A  
· On D és la distància que obté el sensor d'ultrasons  
· On A és l'angle en el que es troba el servo motor

_**Enviament de dades de Posició del satèl·lit**_ --> 4:t:x:y:z  
· On t és el temps en un determinat moment
· On x és la posició del satèl·lit respecte l'eix X de la Terra 
· On y és la posició del satèl·lit respecte l'eix Y de la Terra 
· On z és la posició del satèl·lit respecte l'eix Z de la Terra 

_**ERROR de comunicació entre arduinos**_ --> 5:  
En el cas que la comunicació via cable o kit LoRa falli, és a dir, que l'estació de terra no rebi ningún missatge del satèl·lit, salta una alarma

_**ERROR dades DHT**_ --> 6:  
En el cas que el sensor DHT obtingui un valor NaN de temperatures o humitats, salta una alarma

_**ERROR de temperatura alta**_ --> 7:  
En el cas que el sensor DHT obtingui un valor superior al llindar de temperatura establert per l'usuari, salta una alarma

_**ERROR de temperatura alta**_ --> 8:  
En el cas que el sensor DHT obtingui un valor superior al llindar d'humitat establert per l'usuari, salta una alarma

_**ERROR de radar**_ --> 9:  
En el cas que el sensor d'ultrasons rebi un valor de distància NaN, salta una alarma

_**ERROR de perill de xoc**_ --> 10:  
En el cas que el sensor d'ultrasons rebi un valor menor al llindar de distància establert per l'usuari, salta una alarma. També voldrà dir que el satèl·lit esta en perill de col·lisió  


(INSERTAR FOTO DE GRUP 11)
![IMATGE DE GRUP 11](assets/nomdelaimatge)
