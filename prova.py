import serial
import matplotlib.pyplot as plt
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
import numpy as np

temperaturas = []
plt.ion()
eje_x = []
i = 0
plt.axis([0,100,0,40])

device = 'COM6'
mySerial = serial.Serial(device, 9600)

print ("Empezamos")

def comunicacion():
    while True:
         if mySerial.in_waiting > 0:
            linea = mySerial.readline().decode('utf-8').rstrip()
            trozos = linea.split (':')
            print('La temperatura es:', trozos[0],'ºC')
            print('La humedad es:', trozos[1],'%')
        
            eje_x.append (i)
            temperatura = float(trozos[0])
            temperaturas.append (temperatura)

            plt.plot(eje_x,temperaturas)
            plt.title(str(i))

            i = i + 1

            plt.draw()
            plt.pause(0.5)

def INICIAR ():
    print ('Has pulsado el botón INICIAR')
    command = comunicacion

def PAUSAR ():
    print ('Has pulsado el botón PAUSAR')
    mensaje = "Parar"
    mySerial.write(mensaje.encode('utf-8'))
def REANUDAR ():
    print ('Has pulsado el botón REANUDAR')


    root = tk.Tk()
    root.geometry("300x200")
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=10)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    button_funcions_frame = tk.LabelFrame(root, text ='FUNCIONES')
    button_funcions_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    button_funcions_frame.rowconfigure(0, weight=1)
    button_funcions_frame.rowconfigure(1, weight=1)
    button_funcions_frame.rowconfigure(2, weight=1)
    button_funcions_frame.columnconfigure(0, weight=1)

    button1 = tk.Button(button_funcions_frame, text="INICIAR", command=comunicacion) # FALTA DEFINIR SHOW_DATA (MOSTRAR DADES)
    button1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    button2 = tk.Button(button_funcions_frame, text="INICIAR", command=PAUSAR) # FALTA DEFINIR NOT_SHOW_DATA (NO MOSTRAR DADES)
    button2.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    button3 = tk.Button(button_funcions_frame, text="INICIAR", command=INICIAR) # FALTA DEFINIR SHOW_DATA (NO MOSTRAR DADES)
    button3.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)