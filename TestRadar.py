#--------------------------------------------------
# GRAFICA RADAR
#--------------------------------------------------



def show_graf_radar():
    global ax_radar, fig_radar, angles, distancies, canvas_radar, canvas_graf_radar, graf_actual
    global linia_objecte, punt_objecte

    graf_actual = "radar"

    linia_objecte = None
    punt_objecte = None

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
    global i, angle, distancia, graf_actual, canvas_radar
    global angles, distancies
    global linia_objecte, punt_objecte

    # Substituir o afegir la lectura per a l'angle actual
    lectures_angles[angle] = distancia

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