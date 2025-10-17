import serial
import matplotlib.pyplot as plt
from tkinter import *
import threading

temperaturas = []
plt.ion()
eje_x = []
i = 0
leyendo = False

plt.axis([0,100,0,40])

device = 'COM6'
mySerial = serial.Serial(device, 9600)

print ("Empezamos")

def lectura_datos():
    global i, leyendo
    leyendo = True
    while leyendo: 
        try: 
            if mySerial.in_waiting > 0:
                linea = mySerial.readline().decode('utf-8').rstrip()
                trozos = linea.split (':')
                print('La temperatura es:', trozos[0],'ºC')
                print('La humedad es:', trozos[1],'%')
                        
                eje_x.append (i)
                temperatura = float(trozos[0])
                temperaturas.append (temperatura)

                plt.plot(eje_x,temperaturas, color ='blue')
                plt.title(str(i))

                i = i + 1

                plt.draw()
                plt.pause(0.5)
        except:
              print("No se recibe información")

def INICIAR ():
    global leyendo
    if not leyendo:
        print('Has pulsado el botón INICIAR')
        leyendo = True
        thread = threading.Thread(target=lectura_datos,)
        thread.start()
    
def PAUSAR ():
                global leyendo
                leyendo = False
                print ('Has pulsado el botón PAUSAR')
                mensaje = "Pausar"
                mySerial.write(mensaje.encode('utf-8'))


window = Tk()
window.geometry("200x300")
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)

tituloLabel = Label(window, text = "Mi programa", font=("Courier", 20, "italic"))
tituloLabel.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)


INICIARButton = Button(window, text="INICIAR", bg='red', fg='white', command=lectura_datos)
INICIARButton.grid(row=2, column=0, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)

PAUSARButton = Button(window, text="PAUSAR", bg='yellow', fg="black",command=PAUSAR)
PAUSARButton.grid(row=2, column=1, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)

REANUDARButton = Button(window, text="REANUDAR", bg='blue', fg="white",command=lectura_datos)
REANUDARButton.grid(row=2, column=2, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)


window.mainloop()