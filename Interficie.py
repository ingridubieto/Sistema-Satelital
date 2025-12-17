import tkinter as tk
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import threading
#from queue import Queue
from collections import deque
import sys
import re
import matplotlib
import os
from matplotlib.figure import Figure
import matplotlib.image as mpimg
import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial

device = 'COM11'
baudrate = 9600
mySerial = serial.Serial(device, baudrate, timeout=1)
temperatura = None
mitjana_temperatura = None
mitjana_temperatura_satel·lit = None
mitjana_humitat_satel·lit = None
mitjana_humitat = None
mitjana_python_activa = False
mitjana_arduino_activa = False
cua_mitjanes_temperatura = deque(maxlen = 10)
cua_mitjanes_humitat = deque(maxlen = 10)
humitat = None
distancia = None
angle = None
graf_DHT_actual = None
graf_radar_actual = None
graf_pos_actual = None
i = 0
Comunicacio = True
lectures_angles = {}
x_data = []
y_data = []
z_data = []
fig_map = None
ax_map = None
sat_point = None
sat_trail = None
lat_list = []
lon_list = []
ax_3d = None

FITXER = "esdeveniments.txt"

#--------------------------------------------------
#Dades rebudes (de Satèl·lit a Python)
#--------------------------------------------------

Comando_TyH = 1
Comando_mTymH = 2
Comando_DyA = 3
Comando_txyz = 4
Comando_ErrorCom = 5
Comando_ErrorDHT = 6
Comando_ErrorTempAlta = 7
Comando_ErrorHumAlta = 8
Comando_ErrorRadar = 9
Comando_ErrorXoc = 10


#--------------------------------------------------
#Dades enviades (de Python a Satèl·lit)
#--------------------------------------------------

ComandoT_Parar = "1:"
ComandoT_Reanudar = "2:"
ComandoT_Periode_TyHyD = "3:"
ComandoT_Periode_Pos = "4:"
ComandoT_MitjanesSat = "5:"
ComandoT_MaxTemp = "6:"
ComandoT_MaxHum = "7:"
ComandoT_ServoAuto = "8:"
ComandoT_ServoJoy = "9:"
ComandoT_ServoManual = "10:"
ComandoT_MaxDist = "11:"

#--------------------------------------------------
#Checksum
#--------------------------------------------------

def CompararChecksum(missatge):
    tros = missatge.split("|")
    paraula = tros[0]
    num = int(tros[1])

    resultat = Checksum(paraula)

    if resultat != num:
        return False
    else:
        return True

def Checksum(paraula):
    suma = 0
    for i in range(len(paraula)):
        suma = suma + ord(paraula[i])
    resultat = suma % 256
    
    return resultat

#--------------------------------------------------
#Lectura dades
#--------------------------------------------------

def lectura_datos():
    global Comunicacio, checksum_rebut
    while True: # Aplicar el protocol d'aplicació
            try:
                if mySerial.in_waiting > 0:
                    linea = mySerial.readline().decode('utf-8').strip()

                    if CompararChecksum(linea) == True:
                        dades, checksum_rebut = linea.split('|') # Separem el checksum de les dades del satèl·lit
                        trozos = dades.split(':')                  
                        print(linea)
                        global comando
                        comando = int(trozos[0]) # Determina el tipo de mensaje que recibe la estacion de tierra
                        if comando == Comando_TyH: #1:T:H --> DADES DE TEMPERATURA I HUMITAT
                            global temperatura, humitat
                            temperatura = float(trozos[1]) # 1:T:H --> T es temperatur+a
                            humitat = float(trozos[2]) # 1:T:H --> H es humedad

                        elif comando == Comando_mTymH: #2:mT:mH --> MITJANA DE TEMPERATURES I HUMITATS
                            global mitjana_temperatura_satel·lit, mitjana_humitat_satel·lit
                            mitjana_temperatura_satel·lit = float(trozos[1]) # 2:mT:mH --> mT es la mitjana de les temperatures
                            mitjana_humitat_satel·lit = float(trozos[2]) # 2:mT:mH --> mH es la mitjana de les humitats

                        elif comando == Comando_DyA: # 3:D:A --> DADES DE DISTÀNCIA I ANGLE
                            global distancia, angle
                            distancia = float(trozos[1]) # 3:D:A --> D es distancia i A es angle
                            angle = np.deg2rad(float(trozos[2])) # --> Passa l'angle en graus a radiants

                        elif comando == Comando_txyz: # 4:t:x:y:z --> DADES DE POSICIÓ DEL SATÈL·LIT
                            global t, x, y, z
                            t = float(trozos[1]) # 4:t:x:y:z --> t es temps
                            x = float(trozos[2])
                            y = float(trozos[3])
                            z = float(trozos[4])
                        elif comando == Comando_ErrorCom:
                            alarma1()
                        elif comando == Comando_ErrorDHT:
                            alarma2()
                        elif comando == Comando_ErrorTempAlta:
                            alarma3()
                        elif comando == Comando_ErrorHumAlta:
                            alarma4()
                        elif comando == Comando_ErrorRadar:
                            alarma5()
                        elif comando == Comando_ErrorXoc:
                            alarma6()
                            
            except:
                print("Error de lectura")
            time.sleep(0.1)

thread1 = threading.Thread(target=lectura_datos, daemon=True)
thread1.start()

#--------------------------------------------------
#GRAFICA TEMPERATURA
#--------------------------------------------------

def show_graf_temp ():
    global ax_temp, fig_temp, line_temperatura, line_mitjana_temperatura, temps, temperatures, i, x_max, canvas_temp, canvas_graf_temp, graf_DHT_actual, mitjana_temperatures
    graf_DHT_actual = "temp"

    if 'canvas_graf_hum' in globals() and canvas_graf_hum:
        canvas_graf_hum.grid_forget()

    if 'canvas_graf_temp' in globals() and canvas_graf_temp:
        canvas_graf_temp.grid(row=0, column=0, sticky="nsew")
        return

    fig_temp, ax_temp = plt.subplots()
    ax_temp.set_xlim(0, 20)     # Mostra inicialment 20 mesures
    ax_temp.set_ylim(0, 100)    # Rang de temperatura

    (line_temperatura,) = ax_temp.plot([], [], color='red')
    (line_mitjana_temperatura,) = ax_temp.plot([], [], color='blue', alpha = 0.5)

    # --- Llistes de dades ---
    temps = []
    temperatures = []
    mitjana_temperatures = []

    i = 0
    x_max = 20  # Mida inicial de l’eix X
    canvas_temp = FigureCanvasTkAgg(fig_temp, master = graf_DHT_frame)
    canvas_temp.draw()
    canvas_graf_temp = canvas_temp.get_tk_widget()
    canvas_graf_temp.config(width = 600, height = 400)
    canvas_graf_temp.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

    actualitzar_graf_temp()


def actualitzar_graf_temp():
    global i, x_max, graf_DHT_actual, cua_mitjanes_temperatura, mitjana_temperatura
    
    if graf_DHT_actual != "temp":
        window.after(500, actualitzar_graf_temp)
        return

    if Comunicacio == True:
        try:
            if temperatura is not None:
                #print("Append temperatura", type (temps), type (temperatures))
                temps.append(i)
                temperatures.append(temperatura)
                i += 1

                calcular_mitjana(temperatura, cua_mitjanes_temperatura, mitjana_python_activa, mitjana_arduino_activa, mitjana_temperatura_satel·lit, mitjana_temperatures)


                # Amplia l'eix
                if i > x_max:
                    x_max += 1  # incrementa el límit X de 1 en 1
                    ax_temp.set_xlim(0, x_max)

                # Actualitza dades
                line_temperatura.set_data(temps, temperatures)
                if mitjana_python_activa or mitjana_arduino_activa:
                    line_mitjana_temperatura.set_data(temps, mitjana_temperatures)

                # Escala automàtica de Y segons les dades
                ax_temp.set_ylim(min(temperatures) - 2, max(temperatures) + 2)

                # Actualitza el títol
                ax_temp.set_title(f"Lectura {i}: {temperatura:.2f} °C")
                canvas_temp.draw()

        except Exception as e:
            print("ERROR", e)
            pass

    window.after(500, actualitzar_graf_temp)

#--------------------------------------------------
#GRAFICA HUMITAT
#--------------------------------------------------

def show_graf_hum():
    global ax_hum, fig_hum, line_humitat, temps, humitats, i, x_max, canvas_hum, canvas_graf_hum, graf_DHT_actual, mitjana_humitats, line_mitjana_humitat
    graf_DHT_actual = "hum"

    if 'canvas_graf_temp' in globals() and canvas_graf_temp:
        canvas_graf_temp.grid_forget()

    if 'canvas_graf_hum' in globals() and canvas_graf_hum:
        canvas_graf_hum.grid(row=0, column=0, sticky="nsew")
        return

    fig_hum, ax_hum = plt.subplots()
    ax_hum.set_xlim(0, 20)     # Mostra inicialment 20 mesures
    ax_hum.set_ylim(0, 100)    # Rang de temperatura

    (line_humitat,) = ax_hum.plot([], [], color='blue')
    (line_mitjana_humitat,) = ax_hum.plot([], [], color='yellow', alpha = 0.5)

    # --- Llistes de dades ---
    temps = []
    humitats = []
    mitjana_humitats = []

    i = 0
    x_max = 20  # Mida inicial de l’eix X
    canvas_hum = FigureCanvasTkAgg(fig_hum, master = graf_DHT_frame)
    canvas_hum.draw()
    canvas_graf_hum = canvas_hum.get_tk_widget()
    canvas_graf_hum.config(width = 600, height = 400)
    canvas_graf_hum.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

    actualitzar_graf_hum()


def actualitzar_graf_hum():
    global i, x_max, graf_DHT_actual, cua_mitjanes_humitat
    global mitjana_humitats, mitjana_humitat

    if graf_DHT_actual != "hum":
        window.after(500, actualitzar_graf_hum)
        return

    if Comunicacio == True:
        try:
            if humitat is not None:
                temps.append(i)
                humitats.append(humitat)
                i += 1

                # MITJANA EN PYTHON (CORREGIDA)
                calcular_mitjana(humitat, cua_mitjanes_humitat, mitjana_python_activa, mitjana_arduino_activa, mitjana_humitat_satel·lit, mitjana_humitats)
                # Ampliació de l’eix X
                if i > x_max:
                    x_max += 1
                    ax_hum.set_xlim(0, x_max)

                # Actualització de dades
                line_humitat.set_data(temps, humitats)
                if mitjana_python_activa or mitjana_arduino_activa:
                    line_mitjana_humitat.set_data(temps, mitjana_humitats)

                # Escala Y
                ax_hum.set_ylim(min(humitats) - 2, max(humitats) + 2)

                # Títol
                ax_hum.set_title(f"Lectura {i}: {humitat:.2f} %")

                canvas_hum.draw()

        except Exception as e:
            print("ERROR", e)

    window.after(500, actualitzar_graf_hum)

def calcular_mitjana(valor_actual, cua_python, mitjana_python_activa, mitjana_arduino_activa, mitjana_arduino, llista_resultats):
    if mitjana_python_activa:
        cua_python.append(valor_actual)
        mitjana = sum(cua_python) / len(cua_python)
        llista_resultats.append(mitjana)
    elif mitjana_arduino_activa:
        llista_resultats.append(mitjana_arduino)
    else:
        llista_resultats.append(None)

#--------------------------------------------------
# GRAFICA RADAR
#--------------------------------------------------

def show_graf_radar():
    global ax_radar, fig_radar, angles, distancies, canvas_radar, canvas_graf_radar, graf_radar_actual
    global linia_objecte, punt_objecte, linia_historial

    graf_radar_actual = "radar"

    linia_objecte = None
    punt_objecte = None
    linia_historial = None

    # --- Configuració bàsica ---
    fig_radar = plt.figure()
    ax_radar = plt.subplot(projection='polar')
    ax_radar.set_title("Radar d'Ultrasons", va='bottom')

    # Llistes globals per guardar historial
    angles = []
    distancies = []

    # --- Configuració del radar ---
    ax_radar.set_thetamin(0)
    ax_radar.set_thetamax(180)
    ax_radar.set_theta_direction(-1)
    ax_radar.set_theta_offset(np.pi)
    ax_radar.set_rmax(50)
    ax_radar.set_ylim(0, 50)      # <- limita el radi entre 0 i 50 FIX
    ax_radar.set_rticks([10, 20, 30, 40, 50])

    # Crear canvas
    canvas_radar = FigureCanvasTkAgg(fig_radar, master=graf_radar_frame)
    canvas_graf_radar = canvas_radar.get_tk_widget()
    canvas_graf_radar.config(width=600, height=400)
    canvas_graf_radar.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
    canvas_radar.draw()

    actualitzar_graf_radar()


def actualitzar_graf_radar():
    global i, angle, distancia, graf_radar_actual, canvas_radar
    global angles, distancies
    global linia_objecte, punt_objecte, linia_historial

    try:
        if distancia is not None and angle is not None:

            # Afegim les dades
            lectures_angles[angle] = distancia
            angles_ordenats = sorted(lectures_angles.keys())
            distancies_ordenades = [lectures_angles[a] for a in angles_ordenats]

            # --- ESBORREM LA LÍNIA / PUNT ANTERIORS ---
            if linia_objecte is not None:
                linia_objecte.remove()
                linia_objecte = None

            if punt_objecte is not None:
                punt_objecte.remove()
                punt_objecte = None

            if linia_historial is not None:
                linia_historial.remove()
                punt_objecte = None

            # --- DIBUIXEM NOVA LÍNIA I PUNT ---
            linia_objecte = ax_radar.plot([0, angle], [0, distancia], color='g', linewidth=2)[0]
            punt_objecte = ax_radar.scatter(angle, distancia, color='g', s=80)

            # --- Dibuixar trajectòria ---
            linia_historial = ax_radar.plot(angles_ordenats, distancies_ordenades, color='y', linewidth=2)[0]

            # Actualitzar títol
            ax_radar.set_title(f"Lectura {i}: {np.rad2deg(angle):.1f}º {distancia:.1f} cm")
            
            canvas_radar.draw()

    except Exception as e:
        print("ERROR RADAR", e)

    window.after(500, actualitzar_graf_radar)

#--------------------------------------------------
# GRÀFICA POSICIÓ
#--------------------------------------------------

def ecef_to_latlon(x, y, z):
    R = math.sqrt(x*x + y*y + z*z)
    lat = math.degrees(math.asin(z / R))
    lon = math.degrees(math.atan2(y, x))
    return lat, lon

def show_graf_pos1():
    """Mostra la gràfica 2D de la posició sobre el mapa."""
    global fig_map, ax_map, canvas_map, sat_point, sat_trail
    global lat_list, lon_list, graf_pos_actual

    graf_pos_actual = "map"

    if 'canvas3d' in globals() and canvas3d:
        canvas3d.get_tk_widget().pack_forget()

    # Inicialitzar dades si és la primera vegada
    if 'lat_list' not in globals() or lat_list is None:
        lat_list = []
    if 'lon_list' not in globals() or lon_list is None:
        lon_list = []

    # Si el canvas ja existeix, només el fem visible
    if 'canvas_map' in globals() and canvas_map is not None:
        canvas_map.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return

    # Crear figura
    fig_map = Figure(figsize=(7, 5), dpi=100)
    ax_map = fig_map.add_subplot(111)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path_map = os.path.join(script_dir, "Assets", "world_map.jpg")

    img = mpimg.imread(img_path_map)
    ax_map.imshow(img, extent=[-180, 180, -90, 90])

    ax_map.set_title("Òrbita del satèl·lit")
    ax_map.set_xlabel("Longitud (°)")
    ax_map.set_ylabel("Latitud (°)")
    ax_map.set_xlim(-180, 180)
    ax_map.set_ylim(-90, 90)

    sat_trail, = ax_map.plot([], [], color="yellow", linewidth=2)
    sat_point = ax_map.scatter([], [], color="red", s=40)

    # Integració amb Tkinter
    canvas_map = FigureCanvasTkAgg(fig_map, master=graf_pos_frame)
    canvas_map.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas_map.draw()
    
    #Actualitzem el gràfic
    update_plot_map()

def update_plot_map():
    global sat_point, sat_trail, lat_list, lon_list

    if graf_pos_actual != "map":
        window.after(500, update_plot_map)
        return

    # Convertir ECEF → lat/lon
    lat, lon = ecef_to_latlon(x, y, z)
    #print("Actualitza grafic")
    # Afegir a l'historial
    lat_list.append(lat)
    lon_list.append(lon)
    
    # Detecta salt brusc
    if len(lon_list) > 1 and abs(lon_list[-1] - lon_list[-2]) > 100:
        lat_list.clear()
        lon_list.clear()
        lat_list.append(lat)
        lon_list.append(lon)

    # Actualitza sempre la gràfica
    sat_trail.set_data(lon_list, lat_list)
    sat_point.set_offsets([[lon, lat]])
    canvas_map.draw()


    # Actualitzar línia i punt
    if sat_trail is not None:
        sat_trail.set_data(lon_list, lat_list) 
    if sat_point is not None:
        sat_point.set_offsets([[lon, lat]]) 
    
    canvas_map.draw()

    window.after(500, update_plot_map)
    
R_EARTH = 6371000

u = np.linspace(0, 2*np.pi, 40)
v = np.linspace(0, np.pi, 20)

earth_x = R_EARTH * np.outer(np.cos(u), np.sin(v))
earth_y = R_EARTH * np.outer(np.sin(u), np.sin(v))
earth_z = R_EARTH * np.outer(np.ones_like(u), np.cos(v))


# Globals addicionals
orbit_line = None
sat_point_3d = None

def show_graf_pos2():
    """Mostra la gràfica 3D de la posició."""
    global fig_3d, ax_3d, canvas3d, orbit_line, sat_point_3d, graf_pos_actual

    graf_pos_actual = "3d"

    if 'canvas_map' in globals() and canvas_map:
        canvas_map.get_tk_widget().pack_forget()

    # Si el canvas ja existeix, només el fem visible
    if 'canvas3d' in globals() and canvas3d is not None:
        canvas3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return

    fig_3d = Figure(figsize=(7,6), dpi=100)
    ax_3d = fig_3d.add_subplot(111, projection='3d')

    canvas3d = FigureCanvasTkAgg(fig_3d, master=graf_pos_frame)
    canvas3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Terra
    R_EARTH = 6371000
    u = np.linspace(0, 2*np.pi, 40)
    v = np.linspace(0, np.pi, 20)
    earth_x = R_EARTH * np.outer(np.cos(u), np.sin(v))
    earth_y = R_EARTH * np.outer(np.sin(u), np.sin(v))
    earth_z = R_EARTH * np.outer(np.ones_like(u), np.cos(v))
    ax_3d.plot_wireframe(earth_x, earth_y, earth_z, color='gold', linewidth=0.5, alpha=1)

    ax_3d.set_xlabel("X (m)")
    ax_3d.set_ylabel("Y (m)")
    ax_3d.set_zlabel("Z (m)")
    ax_3d.set_title("Òrbita del satèl·lit (3D)")
    ax_3d.set_box_aspect([1,1,1])

    orbit_line, = ax_3d.plot([], [], [], color='blue')
    sat_point_3d = ax_3d.scatter([], [], [], color='red', s=40)

    canvas3d.draw()

    #Actualitzem el gràfic
    update_plot()

def update_plot():
    global ax_3d, orbit_line, sat_point_3d, graf_pos_actual, canvas3d

    if graf_pos_actual != "3d":
        window.after(500, update_plot)
        return

    if ax_3d is None or len(x_data) < 2:
        return

    # Actualitzar la línia de trajectòria
    orbit_line.set_data(x_data, y_data)
    orbit_line.set_3d_properties(z_data)

    # Actualitzar el punt vermell només a l'última posició
    sat_point_3d._offsets3d = ([x_data[-1]], [y_data[-1]], [z_data[-1]])

    canvas3d.draw_idle()

    window.after(500, update_plot)


def parar_com():
    global Comunicacio
    msg = f"{ComandoT_Parar}|{Checksum(ComandoT_Parar)}"
    mySerial.write(msg.encode())
    Comunicacio = False
    print("Parar")
    escribir_evento("COMANDO", "Parar Emissio de dades")


def reanudar_com():
    global Comunicacio
    msg = f"{ComandoT_Reanudar}|{Checksum(ComandoT_Reanudar)}" # 2 vol dir reanudar l'emissió de dades
    mySerial.write(msg.encode())
    Comunicacio = True
    print("Reanudar")
    escribir_evento("COMANDO", "Reanudar Emissio de dades")


def valor_period_TyH_D_slider():
    valor_period_ = int(period_TyH_D_slider.get())*1000
    print('val com' + str(valor_period_))
    msg = f"{ComandoT_Periode_TyHyD}{valor_period_}|{Checksum(ComandoT_Periode_TyHyD + str(valor_period_))}" # 3 vol dir periodicitat determinada # f serveix per indicar que es una f-string (“formatted string literal”)
    mySerial.write(msg.encode()) # envia el valor de periodicitat --> .encode() transforma cadena de text en bytes
    escribir_evento("COMANDO", "Canvi Periodicitat d'Emissio de dades de Temperatura, Humitat i Distancia")


def valor_period_pos_slider():
    valor_period_ = int(period_pos_slider.get())*1000
    print('val com' + str(valor_period_))
    msg = f"{ComandoT_Periode_Pos}{valor_period_}|{Checksum(ComandoT_Periode_Pos + str(valor_period_))}" # 3 vol dir periodicitat determinada # f serveix per indicar que es una f-string (“formatted string literal”)
    mySerial.write(msg.encode()) # envia el valor de periodicitat --> .encode() transforma cadena de text en bytes
    escribir_evento("COMANDO", "Canvi Periodicitat d'Emissio de dades de Posicio")


def calcul_mitjanes_python():
    global mitjana_python_activa, mitjana_arduino_activa, cua_mitjanes_temperatura, cua_mitjanes_humitat
    if mitjana_python_activa:
        mitjana_python_activa = False
    elif mitjana_python_activa == False:
        cua_mitjanes_temperatura.clear()
        cua_mitjanes_humitat.clear()
        mitjana_python_activa = True
        mitjana_arduino_activa = False
        #ENVIAR MENSAJE DE CANCELACION DE MEDIAS EN EL SATELITE
        escribir_evento("COMANDO", "Canvi Mitjanes des de la interficie")
    

def calcul_mitjanes_arduino():
    global mitjana_python_activa, mitjana_arduino_activa
    if mitjana_arduino_activa:
        mitjana_arduino_activa = False
    elif mitjana_arduino_activa == False:
        mitjana_arduino_activa = True
        mitjana_python_activa = False
        msg = f"{ComandoT_MitjanesSat}|{Checksum(ComandoT_MitjanesSat)}" # 4 vol dir calcular les mitjanes de temperatura i humitat des del satèl·lit
        mySerial.write(msg.encode())
        escribir_evento("COMANDO", "Calcular Mitjanes des del satel.lit")


def parar_mitjanes(): #Parar tots els calculs de mitjanes
    global mitjana_python_activa, mitjana_arduino_activa
    mitjana_arduino_activa = False
    mitjana_python_activa = False
    #ENVIAR MENSAJE DE CANCELACION DE MEDIAS EN EL SATELITE
    escribir_evento("COMANDO", "Parar Emissio de mitjanes")


def valor_temp_max_slider():
    valor_temp_max_ = temp_max_slider.get()
    print('val graf temp' + str(valor_temp_max_))
    msg = f"{ComandoT_MaxTemp}{valor_temp_max_}|{Checksum(ComandoT_MaxTemp + str(valor_temp_max_))}" # 5 vol dir llindar de temperatura màxima
    mySerial.write(msg.encode()) # envia el valor de temperatura màxima que volem detectar
    escribir_evento("COMANDO", "Canvi Llindar de Temperatura Maxima")


def valor_hum_max_slider():
    valor_hum_max_ = hum_max_slider.get()
    print('val graf hum' + str(valor_hum_max_))
    msg = f"{ComandoT_MaxHum}{valor_hum_max_}|{Checksum(ComandoT_MaxHum + str(valor_hum_max_))}" # 6 vol dir llindar d'humitat màxima
    mySerial.write(msg.encode()) # envia el valor d'humitat màxima que volem detectar
    escribir_evento("COMANDO", "Canvi Llindar d'Humitat Maxima")


def auto_radar(): # Mode automatic del servo tot sol recorre de 0 a 180, com un radar normal
    msg = f"{ComandoT_ServoAuto}|{Checksum(ComandoT_ServoAuto)}" # 7 vol dir mode automatic/constant
    mySerial.write(msg.encode())
    print('Mode Automatic')
    escribir_evento("COMANDO", "Mode Automatic del Radar")

def joystick_radar():
    msg = f"{ComandoT_ServoJoy}|{Checksum(ComandoT_ServoJoy)}" # 8 vol dir mode joystick
    mySerial.write(msg.encode())
    print('Mode Joystick')
    escribir_evento("COMANDO", "Mode Joystick del Radar")


def valor_radar_slider(): # Mode manual del servo, es dirigeix al valor d'angle que indiques
    valor_ = radar_slider.get()
    print('val radar' + str(valor_))
    msg = f"{ComandoT_ServoManual}{valor_}|{Checksum(ComandoT_ServoManual + str(valor_))}" # 9 vol dir angle determinat
    mySerial.write(msg.encode()) # envia el valor de l'angle
    escribir_evento("COMANDO", "Mode Manual del Radar")


def valor_dist_max_slider():
    valor_dist_max_ = dist_max_slider.get()
    print('val graf dist' + str(valor_dist_max_))
    msg = f"{ComandoT_MaxDist}{valor_dist_max_}|{Checksum(ComandoT_MaxDist + str(valor_dist_max_))}" # 6 vol dir llindar d'humitat màxima
    mySerial.write(msg.encode()) # envia el valor d'humitat màxima que volem detectar
    escribir_evento("COMANDO", "Canvi Llindar de Distancia Maxima")


#--------------------------------------------------
#ALARMES
#--------------------------------------------------

def alarma1():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Comunciació') # Fallo en la comunicació Satél·lit-Terra
    print('ERROR COMUNICACIÓ')
    escribir_evento("ALARMA", "Comunicacio Arduinos")

def alarma2():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Dades DHT') # Fallo en captar les dades de Temperatura i Humitat
    print('ERROR SENSOR DHT')
    escribir_evento("ALARMA", "No es capta Temperatura ni Humitat correctament")

def alarma3():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Temperatura Alta')# Quan la temperatura excedeix X ºC
    print('ERROR TEMPERATURA ALTA')
    escribir_evento("ALARMA", "Temperatura Alta")

def alarma4():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message="Alarma d'Humitat Alta") # Quan l'humitat excedeix X %
    print('ALERTA HUMITAT ALTA')
    escribir_evento("ALARMA", "Humitat Alta")

def alarma5():
    window.bell()
    #messagebox.showwarning(title='Sistema Satelital', message='Alarma de Radar') # Fallo en captar les dades de Distancia
    print('ERROR RADAR')
    escribir_evento("ALARMA", "No es capta Distancia ni Angle correctament")

def alarma6():
    window.bell()
    messagebox.showwarning(title='Sistema Satelital', message="Alarma Perill de Xoc") # Quan la distància excedeix X cm/m
    print('ALERTA XOC')
    escribir_evento("ALARMA", "Perill de Xoc amb Objecte Espacial")

#--------------------------------------------------
#FITXER
#--------------------------------------------------

def escribir_evento(tipo, descripcion):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FITXER, "a") as f:
        f.write(f"{fecha} | {tipo} | {descripcion}\n")

def guardar_observacion():
    texto = entrada_obs.get()
    if texto.strip():
        escribir_evento("OBSERVACION", texto)
        entrada_obs.delete(0, tk.END)

def filtrar_esdeveniments():
    tipo = str(var_tipo.get())
    fecha = str(entrada_date.get().strip())

    fitxer_entrada = None
    fitxer_sortida = None

    try:
        fitxer_entrada = open(FITXER, 'r')
        fitxer_sortida = open('filtres.txt', 'w')
        for linea in fitxer_entrada.readlines():
            trossos = linea.split('|')
            data_hora = trossos[0]
            data = data_hora.split(' ')[0]
            event = trossos[1].strip() # treu espais als extrems del tipus d'esdeveniments

            if (fecha == data or fecha == '') and (tipo == event or tipo == "TODOS"):
                fitxer_sortida.write(linea)

    except FileNotFoundError:
        print("No hi ha events registrats.")
    finally:
        if fitxer_entrada is not None:
            fitxer_entrada.close()
        if fitxer_sortida is not None:
            fitxer_sortida.close()

    try:
        with open('filtres.txt', 'r') as f:
            contingut = f.read()
        salida.delete('1.0', tk.END)  # netegem el Text
        salida.insert(tk.END, contingut)  # inserim el contingut
    except FileNotFoundError:
        salida.delete('1.0', tk.END)
        salida.insert(tk.END, "No hi ha resultats per mostrar.")

#Configuració finestra interfaç
window = tk.Tk()
window.geometry("1000x400")
window.title("Sistema Satelital")

#Matriu distribució
# 4 files del mateix pes
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)

# 3 columnes de pes diferent
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=10)
window.columnconfigure(2, weight=1)


########## Definició primera columna botons
#Frame comunciacions
button_com_frame = tk.LabelFrame(window, text = 'Comuncacions')
button_com_frame.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_com_frame.rowconfigure(0, weight = 1)
button_com_frame.rowconfigure(1, weight = 1)
button_com_frame.rowconfigure(2, weight = 1)
button_com_frame.columnconfigure(0, weight = 1)

#SubFrame de comunicacions --> Frame periodicitat
button_period_com_frame = tk.LabelFrame(button_com_frame, text = 'Periodicitat')
button_period_com_frame.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_period_com_frame.rowconfigure(0, weight = 1)
button_period_com_frame.rowconfigure(1, weight = 1)
button_period_com_frame.columnconfigure(0, weight = 1)
button_period_com_frame.columnconfigure(1, weight = 1)


#Frame de DHT
button_DHT_frame = tk.LabelFrame(window, text = 'DHT')
button_DHT_frame.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_DHT_frame.rowconfigure(0, weight = 1)
button_DHT_frame.rowconfigure(1, weight = 1)
button_DHT_frame.rowconfigure(2, weight = 1)
button_DHT_frame.rowconfigure(3, weight = 2)
button_DHT_frame.columnconfigure(0, weight = 1)

#SubFrame de DHT --> Frame càlcul mitjanes
button_mitj_DHT_frame = tk.LabelFrame(button_DHT_frame, text = 'Càlcul mitjanes')
button_mitj_DHT_frame.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_mitj_DHT_frame.rowconfigure(0, weight = 1)
button_mitj_DHT_frame.columnconfigure(0, weight = 1)
button_mitj_DHT_frame.columnconfigure(1, weight = 1)

#SubFrame de DHT --> Frame llindars màxims d'alerta
button_max_DHT_frame = tk.LabelFrame(button_DHT_frame, text = "Llindars màxims d'alerta")
button_max_DHT_frame.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_max_DHT_frame.rowconfigure(0, weight = 1)
button_max_DHT_frame.rowconfigure(1, weight = 1)
button_max_DHT_frame.columnconfigure(0, weight = 1)


#Frame de radar
button_radar_frame = tk.LabelFrame(window, text = 'Radar')
button_radar_frame.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_radar_frame.rowconfigure(0, weight = 1)
button_radar_frame.rowconfigure(1, weight = 1)
button_radar_frame.columnconfigure(0, weight = 1)

#SubFrame de radar --> Frame mode servomotor
button_mode_radar_frame = tk.LabelFrame(button_radar_frame, text = 'Mode')
button_mode_radar_frame.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_mode_radar_frame.rowconfigure(0, weight = 1)
button_mode_radar_frame.rowconfigure(1, weight = 1)
button_mode_radar_frame.columnconfigure(0, weight = 1)
button_mode_radar_frame.columnconfigure(1, weight = 1)

#SubFrame de radar --> Frame llindar màxim d'alerta
button_max_radar_frame = tk.LabelFrame(button_radar_frame, text = "Llindar màxim d'alerta")
button_max_radar_frame.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_max_radar_frame.rowconfigure(0, weight = 1)
button_max_radar_frame.columnconfigure(0, weight = 1)
button_max_radar_frame.columnconfigure(1, weight = 1)


#Frame de posició
button_pos_frame = tk.LabelFrame(window, text = 'Posició')
button_pos_frame.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_pos_frame.rowconfigure(0, weight = 1)
button_pos_frame.columnconfigure(0, weight = 1)
button_pos_frame.columnconfigure(1, weight = 1)


#BOTONS COMUNICACIÓ
#Boto parar
button_parar = tk.Button(button_com_frame, text = "Parar", command = parar_com)
button_parar.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Boto reanudar
button_reanudar = tk.Button(button_com_frame, text = "Reanudar", command = reanudar_com)
button_reanudar.grid(row = 1, column = 0, columnspan = 2 , padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Slider frequencia enviament temperatures, humitats i distàncies
period_TyH_D_slider = Scale(button_period_com_frame, from_ = 1, to = 10, orient = HORIZONTAL, width = 10)
period_TyH_D_slider.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = 'ew')
botton_period_TyH_D_slider = Button(button_period_com_frame, text = 'Valor', command = valor_period_TyH_D_slider)
botton_period_TyH_D_slider.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = 'ew')

#Slider frequencia enviament posició del satèl·lit
period_pos_slider = Scale(button_period_com_frame, from_ = 1, to = 10, orient = HORIZONTAL, width = 10)
period_pos_slider.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = 'ew')
botton_period_pos_slider = Button(button_period_com_frame, text = 'Valor', command = valor_period_pos_slider)
botton_period_pos_slider.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = 'ew')


#BOTONS GRAFIQUES TEMPERATURA I HUMITAT
#Boto graf temp
button_temp = tk.Button(button_DHT_frame, text = "Mostrar gràfica temperatura", command = show_graf_temp)
button_temp.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Boto graf humitat
button_hum = tk.Button(button_DHT_frame, text = "Mostrar gràfica humitat", command = show_graf_hum)
button_hum.grid(row = 1, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Botons de càlcul mitjanes Sat
button_cal_arduino = tk.Button(button_mitj_DHT_frame, text = 'Satèl·lit', command = calcul_mitjanes_arduino)
button_cal_arduino.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Botons de càlcul mitjanes Python
button_cal_py = tk.Button(button_mitj_DHT_frame, text = 'Terra', command = calcul_mitjanes_python)
button_cal_py.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Slider Temperatura màxima
temp_max_slider = Scale(button_max_DHT_frame, from_ = 15, to = 50, orient = HORIZONTAL, width = 10) # width=10 --> tamany de la "rodeta"
temp_max_slider.grid(row = 0, column = 0, padx = 5, pady = 1, sticky = 'ew')
botton_graf_slider = Button(button_max_DHT_frame, text = 'Valor de Temp', command = valor_temp_max_slider)#Important command
botton_graf_slider.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = 'ew')

#Slider Humitat màxima
hum_max_slider = Scale(button_max_DHT_frame, from_ = 40, to = 80, orient = HORIZONTAL, width = 10) # width=10 --> tamany de la "rodeta"
hum_max_slider.grid(row = 1, column = 0, padx = 5, pady = 1, sticky = 'ew')
botton_graf_slider = Button(button_max_DHT_frame, text = 'Valor de Hum', command = valor_hum_max_slider)#Important command
botton_graf_slider.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = 'ew')


#BOTONS RADAR
#Boto grafica radar
button_radar = tk.Button(button_radar_frame, text = "Mostrar gràfica radar", command = show_graf_radar)
button_radar.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = 'nsew')

#Boto moviment radar (Mode automatic)
button_auto_radar = tk.Button(button_mode_radar_frame, text = "Automàtic", command = auto_radar)
button_auto_radar.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Boto moviment radar (Mode joystick)
button_joystick_radar = tk.Button(button_mode_radar_frame, text = "Joystick", command = joystick_radar)
button_joystick_radar.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Slidder moviment radar (Mode manual)
radar_slider = Scale(button_mode_radar_frame, from_ = 0, to = 180, orient = HORIZONTAL, width = 10)
radar_slider.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = 'ew')
botton_radar_slider = Button(button_mode_radar_frame, text = 'Valor', command = valor_radar_slider)
botton_radar_slider.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = 'ew')

#Slidder Distància màxima
dist_max_slider = Scale(button_max_radar_frame, from_ = 10, to = 50, orient = HORIZONTAL, width = 10) # width=10 --> tamany de la "rodeta"
dist_max_slider.grid(row = 0, column = 0, padx = 5, pady = 1, sticky = 'ew')
botton_graf_slider = Button(button_max_radar_frame, text = 'Valor de Dist', command = valor_dist_max_slider)
botton_graf_slider.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = 'ew')


##BOTONS POSICIÓ
#Boto gràfica òrbita + Terra
button_pos1 = tk.Button(button_pos_frame, text = "Òrbita en 2D", command = show_graf_pos1)
button_pos1.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

#Boto gràfica òrbita (GMAT)
button_pos2 = tk.Button(button_pos_frame, text = "Òrbita en 3D", command = show_graf_pos2)
button_pos2.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)


########## Definició segona columna gràfiques
graf_frame = tk.LabelFrame(window, text = 'Gràfiques')
graf_frame.grid(row = 0, column = 1, rowspan = 4, padx = 5, pady = 5, sticky = "nsew")
graf_frame.rowconfigure(0, weight = 1)
graf_frame.rowconfigure(1, weight = 1)
graf_frame.columnconfigure(0, weight = 1)
graf_frame.columnconfigure(1, weight = 1)

#SubFrame de gràfiques --> Frame sensor DHT
graf_DHT_frame = tk.LabelFrame(graf_frame, text = 'Sensor DHT')
graf_DHT_frame.grid(row = 0, column = 0, columnspan =2, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
graf_DHT_frame.rowconfigure(0, weight = 1)
graf_DHT_frame.columnconfigure(0, weight = 1)

#SubFrame de gràfiques --> Frame radar
graf_radar_frame = tk.LabelFrame(graf_frame, text = 'Radar')
graf_radar_frame.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
graf_radar_frame.rowconfigure(0, weight = 1)
graf_radar_frame.rowconfigure(1, weight = 1)
graf_radar_frame.columnconfigure(0, weight = 1)
graf_radar_frame.columnconfigure(1, weight = 1)

#SubFrame de gràfiques --> Frame posició
graf_pos_frame = tk.LabelFrame(graf_frame, text = 'Posició')
graf_pos_frame.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
graf_pos_frame.rowconfigure(0, weight = 1)
graf_pos_frame.columnconfigure(0, weight = 1)


########### Definició tercera columna esdeveniments
#Frame de registre d'esdeveniments
button_esdv_frame = tk.LabelFrame(window, text = "Registre d'esdeveniments")
button_esdv_frame.grid(row = 0, column = 2, rowspan = 2, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_esdv_frame.rowconfigure(0, weight = 1)
button_esdv_frame.rowconfigure(1, weight = 1)
button_esdv_frame.rowconfigure(2, weight = 1)
button_esdv_frame.columnconfigure(0, weight = 1)

#SubFrame de registre d'esdeveniments --> Frame d'observació
button_esdv_obs_frame = tk.LabelFrame(button_esdv_frame, text = "Afegir observació")
button_esdv_obs_frame.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_esdv_obs_frame.rowconfigure(0, weight = 1)
button_esdv_obs_frame.rowconfigure(1, weight = 1)
button_esdv_obs_frame.rowconfigure(2, weight = 1)
button_esdv_obs_frame.columnconfigure(0, weight = 1)

#SubFrame de registre d'esdeveniments --> Frame filtre
button_esdv_filt_frame = tk.LabelFrame(button_esdv_frame, text = "Filtrar observació")
button_esdv_filt_frame.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_esdv_filt_frame.rowconfigure(0, weight = 1)
button_esdv_filt_frame.columnconfigure(0, weight = 1)

#SubFrame de registre d'esdeveniments --> Frame filtre
button_esdv_res_frame = tk.LabelFrame(button_esdv_frame, text = "Resultats del filtre")
button_esdv_res_frame.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_esdv_res_frame.rowconfigure(0, weight = 1)
button_esdv_res_frame.columnconfigure(0, weight = 1)


#Frame de crèdits del satèl·lit
button_cred_frame = tk.LabelFrame(window, text = "MIL-090925")
button_cred_frame.grid(row = 2, column = 2, rowspan = 2, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S) #Sticky coordenades cartesianes en extensió tot el que pugui
button_cred_frame.rowconfigure(0, weight = 1)
button_cred_frame.columnconfigure(0, weight = 1)


##BOTONS AFEGIR OBSERVACIONS
#Entrada de text d'observacions
label_obs = tk.Label(button_esdv_obs_frame, text = "Observació:", anchor = "w")
label_obs.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = "w") # anchor="w" i sticky="w", és per posar el label a l'esquerra i no centrat (west)
entrada_obs = tk.Entry(button_esdv_obs_frame, width = 50)
entrada_obs.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = "ew")

#Boto guardar observació introduïda
button_guardar = tk.Button(button_esdv_obs_frame, text = "Guardar observació", anchor = "e" ,command = guardar_observacion)
button_guardar.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = "e") # anchor="e" i sticky="e", és per posar el label a la dreta i no centrat (east)


##BOTONS FILTRAR OBSERVACIONS
#Desplegable tipus d'esdeveniment
label_tipus = tk.Label(button_esdv_filt_frame, text="Tipus d'esdeveniment:")
label_tipus.grid(row=0, column=0, padx=5, pady=5, sticky="w")
var_tipo = tk.StringVar()
var_tipo.set("TODOS") # opcio inicial del desplegable
opcions_tipus = ["TODOS", "ALARMA", "COMANDO", "OBSERVACION"] # opcions del desplegable
menu_tipo = tk.OptionMenu(button_esdv_filt_frame, var_tipo, *opcions_tipus)
menu_tipo.grid(row=0, column=1, sticky="w", padx=5, pady=5)

#Entrada de text de la data
label_date = tk.Label(button_esdv_filt_frame, text = "Filtrar per data (YYYY-MM-DD):", anchor = "w")
label_date.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = "w") # anchor="w" i sticky="w", és per posar el label a l'esquerra i no centrat (west)
entrada_date = tk.Entry(button_esdv_filt_frame, width = 30)
entrada_date.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = "ew")

#Boto aplicar filtres
button_filt = tk.Button(button_esdv_filt_frame, text = "Aplicar filtres", anchor = "e" ,command = filtrar_esdeveniments)
button_filt.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = "e") # anchor="e" i sticky="e", és per posar el label a la dreta i no centrat (east)


##ESPAI DE RESULTATS DEL FILTRE
salida = tk.Text(button_esdv_res_frame, width=30, height=10)
salida.grid(row=0, column=0, padx=5, pady=5, sticky = "nsew")

#Scroll per l'espai del resultats del filtre
scroll = tk.Scrollbar(button_esdv_res_frame, orient="vertical")
scroll.grid(row=0, column=1, sticky="ns")

scroll.config(command=salida.yview)


##ESPAI DE CRÈDITS DEL SATÈL·LIT
# Obtenir el directori on està aquest script
script_dir = os.path.dirname(os.path.abspath(__file__))
img_path_sat = os.path.join(script_dir, "Assets", "MIL-090925.jpg")  # 'Assets' amb majúscula
#Imatge del nostre Satèl·lit
img = Image.open(img_path_sat)
img = img.resize((400, 250))
img_tk = ImageTk.PhotoImage(img)

label = tk.Label(button_cred_frame, image=img_tk, anchor = "w")
label.grid(row = 0, column = 0, sticky = "nsew")

window.mainloop()
