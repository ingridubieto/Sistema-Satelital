import tkinter as tk
from tkinter import *
from tkinter import messagebox
#from PIL import Image#,ImageTK
import time
import threading
#from queue import Queue

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial

device = 'COM3'
baudrate = 9600
mySerial = serial.Serial(device, baudrate, timeout=1)
temperatura = None
humitat = None
distancia = None
angle = None
graf_actual = None

def lectura_datos():
    while True:
        try:
            if mySerial.in_waiting > 0:
                linea = mySerial.readline().decode('utf-8').strip()
                trozos = linea.split(':')
                global comando
                comando = trozos[0] # Determina el tipo de mensaje que recibe la estacion de tierra
                if comando == 1:
                    global temperatura, humitat
                    temperatura = float(trozos[1]) # 1:T:H --> T es temperatura
                    humitat = float(trozos[2]) # 1:T:H --> H es humedad
                elif comando == 2:
                    global distancia, angle
                    distancia = float(trozos[1]) # 2:D:A --> D es distancia A es angle
                    angle = np.deg2rad(float(trozos[2])) # --> Passa l'angle en graus a radians
                elif comando == 3: # 3: --> ERROR SENSOR DHT
                    alarma1()
                elif comando == 4: # 4: --> ERROR RADAR
                    alarma2()
                elif comando == 5: # 5: --> ERROR COMUNICACIÓ
                    alarma3()
                elif comando == 6: # 6: --> TEMPERATURA ALTA
                    alarma4()
        except:
            print("Error de lectura")
        time.sleep(0.1)

thread1 = threading.Thread(target=lectura_datos, daemon=True)
thread1.start()

#--------------------------------------------------
#GRAFICA TEMPERATURA
#--------------------------------------------------

def show_graf_temp ():
    global ax, fig, line, temps, temperatures, i, x_max, canvas, canvas_graf, graf_actual
    graf_actual = "temp"

    if 'canvas_graf' in globals() and canvas_graf.winfo_exists():
        canvas_graf.grid_forget()

    fig, ax = plt.subplots()
    ax.set_xlim(0, 20)     # Mostra inicialment 20 mesures
    ax.set_ylim(0, 100)    # Rang de temperatura

    (line,) = ax.plot([], [], color='red')

    # --- Llistes de dades ---
    temps = []
    temperatures = []

    i = 0
    x_max = 20  # Mida inicial de l’eix X
    canvas = FigureCanvasTkAgg(fig, master = graf_frame)
    canvas.draw()
    canvas_graf = canvas.get_tk_widget()
    canvas_graf.config(width = 600, height = 400)
    canvas_graf.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

    #if 'canvas_graf' in globals():
        #canvas_graf.grid_forget()

    actualitzar_graf_temp()

def actualitzar_graf_temp():
    global i, x_max, graf_actual

    if graf_actual != "temp":
        print("Canvi de graf")
        return

    try:
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

            #if 'canvas_graf' in globals():
                #canvas_graf.grid_forget()

    except Exception as e:
        print("ERROR", e)
        pass

    window.after(500, actualitzar_graf_temp)

#--------------------------------------------------
#GRAFICA HUMITAT
#--------------------------------------------------

def show_graf_hum ():
    global ax, fig, line, temps, humitats, i, x_max, canvas, canvas_graf, graf_actual
    graf_actual = "hum"

    if 'canvas_graf' in globals() and canvas_graf.winfo_exists():
        canvas_graf.grid_forget()

    fig, ax = plt.subplots()
    ax.set_xlim(0, 20)     # Mostra inicialment 20 mesures
    ax.set_ylim(0, 100)    # Rang de temperatura

    (line,) = ax.plot([], [], color='blue')

    # --- Llistes de dades ---
    temps = []
    humitats= []

    i = 0
    x_max = 20  # Mida inicial de l’eix X
    canvas = FigureCanvasTkAgg(fig, master = graf_frame)
    canvas.draw()
    canvas_graf = canvas.get_tk_widget()
    canvas_graf.config(width = 600, height = 400)
    canvas_graf.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

    #if 'canvas_graf' in globals():
        #canvas_graf.grid_forget()

    actualitzar_graf_hum()

def actualitzar_graf_hum():
    global i, x_max, graf_actual

    if graf_actual != "hum":
        print("Canvi de graf")
        return

    try:
        if humitat is not None:
            temps.append(i)
            humitats.append(humitat)
            i += 1

            # Amplia l'eix
            if i > x_max:
                x_max += 1  # incrementa el límit X de 1 en 1
                ax.set_xlim(0, x_max)

            # Actualitza dades
            line.set_data(temps, humitats)

            # Escala automàtica de Y segons les dades
            ax.set_ylim(min(humitats) - 2, max(humitats) + 2)

            # Actualitza el títol
            ax.set_title(f"Lectura {i}: {humitat:.2f} %")
            canvas.draw()



    except Exception as e:
        print("ERROR HUM", e)
        pass

    window.after(500, actualitzar_graf_hum)

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

def parar_com():
    mySerial.write(b"1:\n") # 1 vol dir parar l'emissió de dades
    print('Parar com')

def reanudar_com():
    mySerial.write(b"2:\n") # 2 vol dir reanudar l'emissió de dades
    print('Reanudar com')

def valor_com_slider(): 
    valor_ = com_slider.get()
    print('val com' + str(valor_))
    msg = f"3:{valor_}\n" # 3 vol dir periodicitat determinada # f serveix per indicar que es una f-string (“formatted string literal”)
    mySerial.write(msg.encode()) # envia el valor de periodicitat --> .encode() transforma cadena de text en bytes

def auto_radar(): # Mode automatic del servo tot sol recorre de 0 a 180, com un radar normal
    mySerial.write(b"4:\n") # 4 vol dir mode automatic # b serveix per indicar que es una cadena de bytes (no text)
    print('Mode Automatic')

def valor_radar_slider(): # Mode manual del servo, es dirigeix al valor d'angle que indiques
    valor_ = radar_slider.get()
    print('val radar' + str(valor_))
    msg = f"5:{valor_}\n" # 5 vol dir angle determinat
    mySerial.write(msg.encode()) # envia el valor de l'angle

#--------------------------------------------------
#ALARMES
#--------------------------------------------------

def alarma1():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Dades') # Fallo en captar les dades de Temperatura i Humitat
    print('ERROR SENSOR DHT')

def alarma2():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Radar') # Fallo en captar les dades de Distancia
    print('ERROR RADAR')

def alarma3():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Comunicacions') # Fallo en la comunicació Satél·lit-Terra
    print('ERROR COMUNICACIÓ')

def alarma4():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Temperatura') # Quan la temperatura excedeix X ºC
    print('TEMPERATURA ALTA')

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
button_radar_frame.rowconfigure(1, weight = 1)
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

#Boto grafica radar (Mode automatic)
button_auto_radar = tk.Button(button_radar_frame, text = "AutoRadar", command = auto_radar)
button_auto_radar.grid(row = 1, column = 0, columnspan = 2 , padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

########## Definició segona columna grafica
graf_frame = tk.LabelFrame(window, text = 'Gráficas')
graf_frame.grid(row = 0, column = 1, rowspan = 3, padx = 5, pady = 5, sticky = "nsew")
graf_frame.rowconfigure(0, weight = 1)
graf_frame.columnconfigure(0, weight = 1)

window.mainloop()
