import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import Image#,ImageTK
import time
import threading
from queue import Queue

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial

device = 'COM3'
baudrate = 9600
mySerial = serial.Serial(device, baudrate, timeout=1)
cua_temp = Queue()

def lectura_datos_temperatura():
    try:
        if mySerial.in_waiting > 0:
            linea = mySerial.readline().decode('utf-8').strip()
            trozos = linea.split(':')
            temperatura = float(trozos[0])
            cua_temp.put(temperatura)
            print("miau")
            #return temperatura
    except Exception as e:
        print("Error de lectura:", e)
        return None

def show_graf_temp():
    thread1 = threading.Thread(target=lectura_datos_temperatura, daemon=True)
    thread1.start()
    graf_temp()



def graf_temp ():
    fig, ax = plt.subplots()
    ax.set_xlim(0, 20)     # Mostra inicialment 20 mesures
    ax.set_ylim(0, 100)    # Rang de temperatura

    (line,) = ax.plot([], [], color='blue')

    # --- Llistes de dades ---
    temps = []
    temperatures = []

    i = 0
    x_max = 20  # Mida inicial de l’eix X
    global canvas
    canvas = FigureCanvasTkAgg(fig, master = graf_frame)
    canvas.draw()
    canvas_graf = canvas.get_tk_widget()
    canvas_graf.config(width = 600, height = 400)
    canvas_graf.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

    # --- BUCLE INFINIT ---
    while True:
        
        try:
            temperatura = cua_temp.get_nowait()
            if temperatura is not None:
                temps.append(i)
                temperatures.append(temperatura)
                i += 1

                # Amplia l'eix
                if i > x_max:
                    x_max += 1  # incrementa el límit X de 1 en 1
                    ax.set_xlim(0, x_max)

                # Actualitza dades
                line.set_data(temps, temperatures)

                # Escala automàtica de Y segons les dades
                ax.set_ylim(min(temperatures) - 2, max(temperatures) + 2)

                # Actualitza el títol
                ax.set_title(f"Lectura {i}: {temperatura:.2f} °C")

                canvas.draw()
                if 'canvas_graf' in globals():
                    canvas_graf.grid_forget()
                
                print ('Graf temp')
        except:
            pass

        window.after(500, graf_temp)

def show_graf_hum ():
    print ('Graf hum')

def parar_com():
    print('Parar com')

def reanudar_com():
    print('Reanudar com')

def alarm1():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Dades')
    print('Alarm 1')


def alarm2():
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Comunicacions')
    print('Alarm 2')

def alarm3():
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Temperatura')
    print('Alarm 3')

def alarm4():
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Radar')
    print('Alarm 4')

def valor_com_slider(): 
    valor_ = com_slider.get()
    print('val com' + str(valor_))

def show_graf_radar():
    print('Graf radar')

def valor_radar_slider(): 
    valor_ = radar_slider.get()
    print('val radar' + str(valor_))

#Configuració finestra interfaç
window = tk.Tk()
window.geometry("800x400")
window.title("Sistema Satelital")

#Matriu distribució
# 3 files del mateix pes
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)

# 2 columnes de pes diferent
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=10)

########## Definició primera columna botons
#Frame de botons grafiques
button_graf_frame = tk.LabelFrame(window, text = 'Gráficas')
button_graf_frame.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_graf_frame.rowconfigure(0, weight = 1)
button_graf_frame.rowconfigure(1, weight = 1)
button_graf_frame.columnconfigure(0, weight = 1)

#Frame comunciacions
button_com_frame = tk.LabelFrame(window, text = 'Comuncaciones')
button_com_frame.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_com_frame.rowconfigure(0, weight = 1)
button_com_frame.rowconfigure(1, weight = 1)
button_com_frame.columnconfigure(0, weight = 1)

#Frame alarmes
button_radar_frame = tk.LabelFrame(window, text = 'Radar')
button_radar_frame.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_radar_frame.rowconfigure(0, weight = 1)
button_radar_frame.columnconfigure(0, weight = 1)

#Botons grafiques temp i humitat
#Boto graf temp
button_temp = tk.Button(button_graf_frame, text = "Mostrar temperaturas", command = show_graf_temp)
button_temp.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Boto graf humitat
button_hum = tk.Button(button_graf_frame, text = "Mostrar humedad", command = show_graf_hum)
button_hum.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Botons comunicacio
#Boto parar
button_parar = tk.Button(button_com_frame, text = "Parar", command = parar_com)
button_parar.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Boto reanudar
button_reanudar = tk.Button(button_com_frame, text = "Reanudar", command = reanudar_com)
button_reanudar.grid(row = 1, column = 0, columnspan = 2 , padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Slider frequencia enviament
title_slider = Label(button_com_frame, text = "Frecuecia datos")
title_slider.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = 'ew')
com_slider = Scale(button_com_frame, from_ = 0, to = 10, orient = HORIZONTAL, width = 1)
com_slider.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = 'ew')
botton_com_slider = Button(button_com_frame, text = 'Valor', command = valor_com_slider)
botton_com_slider.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = 'ew')

#Boto grafica radar
button_radar = tk.Button(button_radar_frame, text = "Mostrar radar", command = show_graf_radar)
button_radar.grid(row = 0, column = 0, columnspan = 3, padx = 5, pady = 5, sticky = 'nsew')
radar_slider = Scale(button_radar_frame, from_ = 0, to = 180, orient = HORIZONTAL, width = 1)
radar_slider.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = 'ew')
botton_radar_slider = Button(button_radar_frame, text = 'Valor', command = valor_radar_slider)
botton_radar_slider.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = 'ew')

########## Definició segona columna grafica
graf_frame = tk.LabelFrame(window, text = 'Gráficas')
graf_frame.grid(row = 0, column = 1, rowspan = 3, padx = 5, pady = 5, sticky = "nsew")
graf_frame.rowconfigure(0, weight = 1)
graf_frame.columnconfigure(0, weight = 1)

window.mainloop()