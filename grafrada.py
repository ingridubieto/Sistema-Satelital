import tkinter as tk
from tkinter import *
from tkinter import messagebox
#from PIL import Image#,ImageTK
import time
import threading
#from queue import Queue
from collections import deque


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial

#--------------------------------------------------
#GRAFICA RADAR
#--------------------------------------------------

def show_graf_radar():
    global ax, fig, angles, distancies, canvas, canvas_graf, graf_actual
    graf_actual = "radar"

    if 'canvas_graf' in globals() and canvas_graf.winfo_exists():
        canvas_graf.grid_forget()

    # --- Configuració bàsica ---
    fig = plt.figure()
    ax = plt.subplot(projection='polar')
    ax.set_title("Radar d'Ultrasons", va='bottom')

    angles = []
    distancies = []

    # --- Dibuixem la línia groga del radar (les mesures) ---
    ax.plot(angles, distancies, color='y', linewidth=2) #Canviar valors angles distàncies que sera els obtinguts

    # --- Dibuixem objecte
    ax.plot([0, angle], [0, distancia], color='g', linewidth=2)  # línia verda (expressada com un vector)
    ax.scatter(angle, distancia, color='g', s=80)  # punt verd

    # --- Configuració del radar ---
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_theta_direction(-1)      # direcció horària
    ax.set_theta_offset(np.pi)      # base horitzontal i a baix
    ax.set_rmax(50)                 # radi màxim
    ax.set_rticks([10, 20, 30, 40, 50])  # cercles radials

    canvas.draw()

    actualitzar_graf_radar()

def actualitzar_graf_radar():
    global i, angle, distancia, graf_actual

    if graf_actual != "radar":
        print("Canvi de graf")
        return
   
    try:
        if distancia is not None and angle is not None:


            distancies.append(distancia)
            angles.append(angle)
            i += 1


            ax.plot(angles, distancies, color='y', linewidth=2)
            ax.plot([0, angle], [0, distancia], color='g', linewidth=2)  # línia verda (expressada com un vector)
            ax.scatter(angle, distancia, color='g', s=80)  # punt verd


            ax.set_title(f"Lectura {i}: {angle:.2f}º {distancia:.2f}cm")
            canvas.draw()

    except Exception as e:
        print("ERROR RADAR", e)
        pass

    window.after(500, actualitzar_graf_radar)

def auto_radar(): # Mode automatic del servo tot sol recorre de 0 a 180, com un radar normal
    #mySerial.write(b"4:\n") # 4 vol dir mode automatic # b serveix per indicar que es una cadena de bytes (no text)
    print('Mode Automatic')


def valor_radar_slider(): # Mode manual del servo, es dirigeix al valor d'angle que indiques
    valor_ = radar_slider.get()
    print('val radar' + str(valor_))
    msg = f"5:{valor_}\n" # 5 vol dir angle determinat
    #mySerial.write(msg.encode()) # envia el valor de l'angle

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


#Frame alarmes
button_radar_frame = tk.LabelFrame(window, text = 'Radar')
button_radar_frame.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_radar_frame.rowconfigure(0, weight = 1)
button_radar_frame.rowconfigure(1, weight = 1)
button_radar_frame.rowconfigure(2, weight = 1)
button_radar_frame.rowconfigure(3, weight = 1)
button_radar_frame.columnconfigure(0, weight = 1)



#BOTONS RADAR
#Boto grafica radar
button_radar = tk.Button(button_radar_frame, text = "Mostrar radar", command = show_graf_radar)
button_radar.grid(row = 0, column = 0, columnspan = 3, padx = 5, pady = 5, sticky = 'nsew')


#Boto moviment radar (Mode automatic)
button_auto_radar = tk.Button(button_radar_frame, text = "AutoRadar", command = auto_radar)
button_auto_radar.grid(row = 1, column = 0, columnspan = 2 , padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)


#Slidder moviment radar (Mode manual)
title_slider = Label(button_radar_frame, text = "Posicion radar")
title_slider.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = 'ew') #en una altra fila per no ser tapat pel slider
radar_slider = Scale(button_radar_frame, from_ = 0, to = 180, orient = HORIZONTAL, width = 10)
radar_slider.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = 'ew')
botton_radar_slider = Button(button_radar_frame, text = 'Valor', command = valor_radar_slider)
botton_radar_slider.grid(row = 3, column = 1, padx = 5, pady = 5, sticky = 'ew')


########## Definició segona columna grafica
graf_frame = tk.LabelFrame(window, text = 'Gráficas')
graf_frame.grid(row = 0, column = 1, rowspan = 3, padx = 5, pady = 5, sticky = "nsew")
graf_frame.rowconfigure(0, weight = 1)
graf_frame.columnconfigure(0, weight = 1)


window.mainloop()