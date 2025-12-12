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

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial


device = 'COM8'
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
graf_actual = None
i = 0
Comunicacio = True
lectures_angles = {}

FITXER = "esdeveniments.txt"

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
                        if comando == 1: #1:T:H --> DADES DE TEMPERATURA I HUMITAT
                            global temperatura, humitat
                            temperatura = float(trozos[1]) # 1:T:H --> T es temperatur+a
                            humitat = float(trozos[2]) # 1:T:H --> H es humedad

                        elif comando == 2: #2:mT:mH --> MITJANA DE TEMPERATURES I HUMITATS
                            global mitjana_temperatura_satel·lit, mitjana_humitat_satel·lit
                            mitjana_temperatura_satel·lit = float(trozos[1]) # 2:mT:mH --> mT es la mitjana de les temperatures
                            mitjana_humitat_satel·lit = float(trozos[2]) # 2:mT:mH --> mH es la mitjana de les humitats

                        elif comando == 3: # 3:D:A --> DADES DE DISTÀNCIA I ANGLE
                            global distancia, angle
                            distancia = float(trozos[1]) # 3:D:A --> D es distancia i A es angle
                            angle = np.deg2rad(float(trozos[2])) # --> Passa l'angle en graus a radiants

                        elif comando == 4: # 4:t:x:y:z --> DADES DE POSICIÓ DEL SATÈL·LIT
                            global temps, x, y, z
                            temps = float(trozos[1]) # 4:t:x:y:z --> t es temps
                            x = float(trozos[2])
                            y = float(trozos[3])
                            z = float(trozos[4])

                        elif comando == 5: # 5: --> ERROR COMUNICACIÓ
                            alarma1()
                        elif comando == 6: # 6: --> ERROR DADES DHT
                            alarma2()
                        elif comando == 7: # 7: --> ERROR TEMPERATURA ALTA
                            alarma3()
                        elif comando == 8: # 8: --> ERROR HUMITAT ALTA
                            alarma4()
                        elif comando == 9: #9: --> ERROR DADES RADAR
                            alarma5()
                        elif comando == 10: #10: --> ERROR PERILL DE XOC
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
    global ax, fig, line_temperatura, line_mitjana_temperatura, temps, temperatures, i, x_max, canvas, canvas_graf, graf_actual, mitjana_temperatures, lectures_angles
    graf_actual = "temp"
    lectures_angles = {}

    fig, ax = plt.subplots()
    ax.set_xlim(0, 20)     # Mostra inicialment 20 mesures
    ax.set_ylim(0, 100)    # Rang de temperatura

    (line_temperatura,) = ax.plot([], [], color='red')
    (line_mitjana_temperatura,) = ax.plot([], [], color='blue', alpha = 0.5)

    # --- Llistes de dades ---
    temps = []
    temperatures = []
    mitjana_temperatures = []

    i = 0
    x_max = 20  # Mida inicial de l’eix X
    canvas = FigureCanvasTkAgg(fig, master = graf_DHT_frame)
    canvas.draw()
    canvas_graf = canvas.get_tk_widget()
    canvas_graf.config(width = 600, height = 400)
    canvas_graf.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

    actualitzar_graf_temp()


def actualitzar_graf_temp():
    global i, x_max, graf_actual, cua_mitjanes_temperatura, mitjana_temperatura

    if graf_actual != "temp":
        print("Canvi de graf")
        return
    if Comunicacio == True:
        try:
            if temperatura is not None:
                temps.append(i)
                temperatures.append(temperatura)
                i += 1

                calcular_mitjana(temperatura, cua_mitjanes_temperatura, mitjana_python_activa, mitjana_arduino_activa, mitjana_temperatura_satel·lit, mitjana_temperatures)


                # Amplia l'eix
                if i > x_max:
                    x_max += 1  # incrementa el límit X de 1 en 1
                    ax.set_xlim(0, x_max)

                # Actualitza dades
                line_temperatura.set_data(temps, temperatures)
                if mitjana_python_activa or mitjana_arduino_activa:
                    line_mitjana_temperatura.set_data(temps, mitjana_temperatures)

                # Escala automàtica de Y segons les dades
                ax.set_ylim(min(temperatures) - 2, max(temperatures) + 2)

                # Actualitza el títol
                ax.set_title(f"Lectura {i}: {temperatura:.2f} °C")
                canvas.draw()

        except Exception as e:
            print("ERROR", e)
            pass

    window.after(500, actualitzar_graf_temp)

#--------------------------------------------------
#GRAFICA HUMITAT
#--------------------------------------------------

def show_graf_hum():
    global ax, fig, line_humitat, temps, humitats, i, x_max, canvas, canvas_graf, graf_actual, mitjana_humitats, line_mitjana_humitat
    graf_actual = "hum"

    fig, ax = plt.subplots()
    ax.set_xlim(0, 20)     # Mostra inicialment 20 mesures
    ax.set_ylim(0, 100)    # Rang de temperatura

    (line_humitat,) = ax.plot([], [], color='blue')
    (line_mitjana_humitat,) = ax.plot([], [], color='yellow', alpha = 0.5)

    # --- Llistes de dades ---
    temps = []
    humitats = []
    mitjana_humitats = []

    i = 0
    x_max = 20  # Mida inicial de l’eix X
    canvas = FigureCanvasTkAgg(fig, master = graf_DHT_frame)
    canvas.draw()
    canvas_graf = canvas.get_tk_widget()
    canvas_graf.config(width = 600, height = 400)
    canvas_graf.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.N + tk.E + tk.W + tk.S)

    actualitzar_graf_hum()


def actualitzar_graf_hum():
    global i, x_max, graf_actual, cua_mitjanes_humitat
    global mitjana_humitats, mitjana_humitat

    if graf_actual != "hum":
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
                    ax.set_xlim(0, x_max)

                # Actualització de dades
                line_humitat.set_data(temps, humitats)
                if mitjana_python_activa or mitjana_arduino_activa:
                    line_mitjana_humitat.set_data(temps, mitjana_humitats)

                # Escala Y
                ax.set_ylim(min(humitats) - 2, max(humitats) + 2)

                # Títol
                ax.set_title(f"Lectura {i}: {humitat:.2f} %")

                canvas.draw()

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
    global ax, fig, angles, distancies, canvas, canvas_graf, graf_actual
    global linia_objecte, punt_objecte

    graf_actual = "radar"

    linia_objecte = None
    punt_objecte = None

    # --- Configuració bàsica ---
    fig = plt.figure()
    ax = plt.subplot(projection='polar')
    ax.set_title("Radar d'Ultrasons", va='bottom')

    # Llistes globals per guardar historial
    angles = []
    distancies = []

    # --- Configuració del radar ---
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi)
    ax.set_rmax(50)
    ax.set_ylim(0, 50)      # <- limita el radi entre 0 i 50 FIX
    ax.set_rticks([10, 20, 30, 40, 50])

    # Crear canvas
    canvas = FigureCanvasTkAgg(fig, master=graf_radar_frame)
    canvas_graf = canvas.get_tk_widget()
    canvas_graf.config(width=600, height=400)
    canvas_graf.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
    canvas.draw()

    actualitzar_graf_radar()


def actualitzar_graf_radar():
    global i, angle, distancia, graf_actual, canvas
    global angles, distancies
    global linia_objecte, punt_objecte

    # Substituir o afegir la lectura per a l'angle actual
    lectures_angles[angle] = distancia

    if graf_actual != "radar":
        return

    try:
        if distancia is not None and angle is not None:

            # Afegim les dades
            lectures_angles[angle] = distancia
            angles.append(angle)
            distancies.append(distancia)
            angles_ordenats = sorted(lectures_angles.keys())
            distancies_ordenades = [lectures_angles[a] for a in angles_ordenats]

            # --- ESBORREM LA LÍNIA / PUNT ANTERIORS ---
            if linia_objecte is not None:
                linia_objecte.remove()
            if punt_objecte is not None:
                punt_objecte.remove()

            # --- DIBUIXEM NOVA LÍNIA I PUNT ---
            linia_objecte = ax.plot([0, angle], [0, distancia], color='g', linewidth=2)[0]
            punt_objecte = ax.scatter(angle, distancia, color='g', s=80)

            # --- Dibuixar trajectòria ---
            linia_historial = ax.plot(angles_ordenats, distancies_ordenades, color='y', linewidth=2)[0]

            # Actualitzar títol
            ax.set_title(f"Lectura {i}: {np.rad2deg(angle):.1f}º {distancia:.1f} cm")

            canvas.draw()

    except Exception as e:
        print("ERROR RADAR", e)

    window.after(500, actualitzar_graf_radar)

#--------------------------------------------------
# GRÀFICA POSICIÓ
#--------------------------------------------------

def show_graf_pos1():
    global ax, fig, canvas, canvas_graf, graf_actual
    global earth_slice
    print("Gràfic Òrbita CentrePolar")

    matplotlib.use('TkAgg')

    regex = re.compile(r"Position: \(X: ([\d\.-]+) m, Y: ([\d\.-]+) m, Z: ([\d\.-]+) m\)")

    x_vals = []
    y_vals = []

    R_EARTH = 6371000  # m

    # --- CONFIGURACIÓ FIGURA ---
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=graf_pos_frame)
    canvas_graf = canvas.get_tk_widget()
    canvas_graf.config(width=600, height=400)
    canvas_graf.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    orbit_plot, = ax.plot([], [], 'bo-', label='Satellite Orbit', markersize=2)
    last_point_plot = ax.scatter([], [], color='red', s=50, label='Last Point')

    earth_circle = plt.Circle((0, 0), R_EARTH, color='orange', fill=False, label='Earth Surface')
    ax.add_artist(earth_circle)

    ax.set_xlim(-7e6, 7e6)
    ax.set_ylim(-7e6, 7e6)
    ax.set_aspect('equal', 'box')
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_title('Satellite Equatorial Orbit (View from North Pole)')
    ax.grid(True)
    ax.legend()

    window_closed = False

    def on_close(event):
        nonlocal window_closed
        print("Window closed")
        plt.close(fig)
        window_closed = True

    fig.canvas.mpl_connect('close_event', on_close)

    def draw_earth_slice(z):
        slice_radius = (R_EARTH**2 - z**2)**0.5 if abs(z) <= R_EARTH else 0
        return plt.Circle((0, 0), slice_radius, color='orange', fill=False, linestyle='--')

    # Inicialitzar secció de la Terra
    earth_slice = draw_earth_slice(0)
    ax.add_artist(earth_slice)

    def update_plot():
        global earth_slice

        if window_closed:
            return

        if mySerial.in_waiting > 0:
            line = mySerial.readline().decode('utf-8').rstrip()
            match = regex.search(line)

            if match:
                x = float(match.group(1))
                y = float(match.group(2))
                z = float(match.group(3))

                print(f"X: {x}, Y: {y}, Z: {z}")

                x_vals.append(x)
                y_vals.append(y)

                # Actualitzar línia i últim punt
                orbit_plot.set_data(x_vals, y_vals)
                last_point_plot.set_offsets([[x, y]])

                # Actualitzar secció de la Terra
                earth_slice.remove()
                earth_slice = draw_earth_slice(z)
                ax.add_artist(earth_slice)

                # Auto-redimensionar
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()

                if abs(x) > max(abs(xlim[0]), abs(xlim[1])) or abs(y) > max(abs(ylim[0]), abs(ylim[1])):
                    new_lim = max(abs(x), abs(y)) * 1.1
                    ax.set_xlim(-new_lim, new_lim)
                    ax.set_ylim(-new_lim, new_lim)

                canvas.draw()

        # Repeteix cada 50ms sense blocar Tkinter
        window.after(50, update_plot)

    # Començar actualització contínua
    update_plot()


def show_graf_pos2():
    print("Gràfic Òrbtia GMAT")


def show_graf_pos3():
    print("Gràfic Òrbita + Terra")


def parar_com():
    global Comunicacio
    msg = f"1:|{Checksum("1:")}" # 1 vol dir parar l'emissió de dades
    mySerial.write(msg.encode())
    Comunicacio = False
    print("Parar 1:")
    escribir_evento("COMANDO", "Parar Emissio de dades")


def reanudar_com():
    global Comunicacio
    msg = f"2:|{Checksum("2:")}" # 2 vol dir reanudar l'emissió de dades
    mySerial.write(msg.encode())
    Comunicacio = True
    print("Reanudar 2:")
    escribir_evento("COMANDO", "Reanudar Emissio de dades")


def valor_period_com_slider():
    valor_period_ = int(period_com_slider.get())*1000
    print('val com' + str(valor_period_))
    msg = f"3:{valor_period_}|{Checksum("3:" + str(valor_period_))}" # 3 vol dir periodicitat determinada # f serveix per indicar que es una f-string (“formatted string literal”)
    mySerial.write(msg.encode()) # envia el valor de periodicitat --> .encode() transforma cadena de text en bytes
    escribir_evento("COMANDO", "Canvi Periodicitat d'Emissio de dades")


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
        msg = f"4:|{Checksum("4:")}" # 4 vol dir calcular les mitjanes de temperatura i humitat des del satèl·lit
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
    msg = f"5:{valor_temp_max_}|{Checksum('5:' + str(valor_temp_max_))}" # 5 vol dir llindar de temperatura màxima
    mySerial.write(msg.encode()) # envia el valor de temperatura màxima que volem detectar
    escribir_evento("COMANDO", "Canvi Llindar de Temperatura Maxima")


def valor_hum_max_slider():
    valor_hum_max_ = hum_max_slider.get()
    print('val graf hum' + str(valor_hum_max_))
    msg = f"6:{valor_hum_max_}|{Checksum("6:" + str(valor_hum_max_))}" # 6 vol dir llindar d'humitat màxima
    mySerial.write(msg.encode()) # envia el valor d'humitat màxima que volem detectar
    escribir_evento("COMANDO", "Canvi Llindar d'Humitat Maxima")


def auto_radar(): # Mode automatic del servo tot sol recorre de 0 a 180, com un radar normal
    msg = f"7:|{Checksum("7:")}" # 7 vol dir mode automatic/constant
    mySerial.write(msg.encode())
    print('Mode Automatic')
    escribir_evento("COMANDO", "Mode Automatic del Radar")

def joystick_radar():
    msg = f"8:|{Checksum("8:")}" # 8 vol dir mode joystick
    mySerial.write(msg.encode())
    print('Mode Joystick')
    escribir_evento("COMANDO", "Mode Joystick del Radar")


def valor_radar_slider(): # Mode manual del servo, es dirigeix al valor d'angle que indiques
    valor_ = radar_slider.get()
    print('val radar' + str(valor_))
    msg = f"9:{valor_}|{Checksum("9:"+str(valor_))}" # 9 vol dir angle determinat
    mySerial.write(msg.encode()) # envia el valor de l'angle
    escribir_evento("COMANDO", "Mode Manual del Radar")


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
    messagebox.showwarning(title='Sistema Satelital', message='Alarma de Radar') # Fallo en captar les dades de Distancia
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
button_period_com_frame.columnconfigure(0, weight = 1)


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

#Slider frequencia enviament
period_com_slider = Scale(button_period_com_frame, from_ = 0, to = 10, orient = HORIZONTAL, width = 10)
period_com_slider.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = 'ew')
botton_period_com_slider = Button(button_period_com_frame, text = 'Valor', command = valor_period_com_slider)
botton_period_com_slider.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = 'ew')


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
'''#Imatge del nostre Satèl·lit
img = Image.open("MIL-090925.jpg")
img = img.resize((400, 250))
img_tk = ImageTk.PhotoImage(img)

label = tk.Label(button_cred_frame, image=img_tk, anchor = "w")
label.grid(row = 0, column = 0, sticky = "nsew")'''

window.mainloop()
