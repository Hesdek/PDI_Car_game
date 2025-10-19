#--------------------------------------------------------------------------
#------- HIGHEST GEAR ----------------------------------------------
#------- Procesamiento de mano por camara-------------------------------------------
#------- Por: Daniel Perez    daniel.perez19@udea.edu.co --------------
#-------      Edisson Chamorro    john.chamorro@udea.edu.co -----------------
#-------      Estudiantes Departamento Electrónica y Telecomunicaciones -------------------
#------- Curso B�sico de Procesamiento de Im�genes y Visi�n Artificial-----
#-------  Octubre de 2025--------------------------------------------------

#--------------------------------------------------------------------------
#--1. Inicializo el sistema -----------------------------------------------
#--------------------------------------------------------------------------

# Importar las librerías necesarias
import cv2
import numpy as np
import threading

# Inicializar variables globales para el estado y posición de la mano
state = {"value": "No detectada"}   
position = {"value": "Centro"}      

#--------------------------------------------------------------------------
#--2. Apertura  de camara web -----------------------------------------------
#--------------------------------------------------------------------------
def hand_state():
    #-- Declaración de variables globales
    global state, position

    # --- Abre camara
    cap = cv2.VideoCapture(0)

    #-- Verificar que la cámara esté disponible
    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    #-- Bucle principal de captura de frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
#--------------------------------------------------------------------------
#-- 3. Paso de imagen a espacio de color HSV  ---------------------
#--------------------------------------------------------------------------
        # --- Voltear imagen (efecto espejo) ---
        frame = cv2.flip(frame, 1)

        # --- Convertir a espacio de color HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#--------------------------------------------------------------------------
#-- 4. Aplicar filtro convolucional gaussiano ---------------------
#--------------------------------------------------------------------------
        # --- Rango de colores para piel
        lower_skin = np.array([0, 30, 60], dtype=np.uint8)
        upper_skin = np.array([20, 150, 255], dtype=np.uint8)

        # --- Crear máscara para color de piel
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # --- Aplicar filtro gaussiano a la mascara
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        mask = cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=2)
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)

#--------------------------------------------------------------------------
#-- 5. Determinar posición de la mano ------------------------------------------
#--------------------------------------------------------------------------
        # --- Encontrar contornos ---
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #--- Determinar si hay contornos ---
        if len(contours) == 0:
            state["value"] = "No detectada"
            position["value"] = "Centro"
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # --- Seleccionar contorno más grande ---
        contour = max(contours, key=cv2.contourArea)

        # --- Filtrar objetos no deseados por el area del contorno ---
        # --- Obtener contorno de mano ---
        area = cv2.contourArea(contour)
        if area < 3000 or area > 100000:
            state["value"] = "No detectada"
            position["value"] = "Centro"
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # --- Dibujar contorno principal---
        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

        # --- Calcular centro de la mano---
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cx, cy), 7, (255, 0, 0), -1)
        else:
            cx, cy = 0, 0

        # --- Determinar posición de la mano ---
        width = frame.shape[1]
        left = width // 3
        right = 2 * width // 3

        if cx < left:
            position["value"] = "Izquierda"
        elif cx > right:
            position["value"] = "Derecha"
        else:
            position["value"] = "Centro"
#--------------------------------------------------------------------------
#-- 6. Determinar estado de la mano ------------------------------------------
#--------------------------------------------------------------------------
        # --- Calcular forma convexa ---
        hull = cv2.convexHull(contour, returnPoints=False)
        if hull is not None and len(hull) > 3:
            # --- Calcular defectos de convexidad ---
            defects = cv2.convexityDefects(contour, hull)

            if defects is not None:
                count_defects = 0

                # --- Recorrer los defectos convexos (hendiduras entre los dedos)
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(contour[s][0])
                    end = tuple(contour[e][0])
                    far = tuple(contour[f][0])

                    # --- Calcular los lados del triángulo formado por los puntos del defecto
                    a = np.linalg.norm(np.array(end) - np.array(start))
                    b = np.linalg.norm(np.array(far) - np.array(start))
                    c = np.linalg.norm(np.array(end) - np.array(far))

                    #--- Calcular el ángulo del defecto
                    angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))

                    # --- Determinar si es un dedo levantado
                    if angle <= np.pi / 2:
                        count_defects += 1
                        cv2.circle(frame, far, 5, (0, 0, 255), -1)

                # --- Determinar estado de la mano conbase a los dedos levantados ---
                if count_defects >= 3:
                    state["value"] = "ABIERTA"
                else:
                    state["value"] = "CERRADA"
            else:
                state["value"] = "CERRADA"

#--------------------------------------------------------------------------
#-- 7. Mostrar información en pantalla ------------------------------------------
#--------------------------------------------------------------------------
        # --- Mostrar en texto estado de la mano ---
        cv2.putText(frame, f"Estado: {state['value']}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        # --- Mostrar en texto posición de la mano ---
        cv2.putText(frame, f"Posicion: {position['value']}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # --- Mostrar frame original---
        cv2.namedWindow("Deteccion de Mano", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Deteccion de Mano", 300, 200)
        cv2.moveWindow("Deteccion de Mano", 1000, 100)
        cv2.imshow("Deteccion de Mano", frame)
        # --- Salir con tecla 'q' ---
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # --- Liberar recursos ---
    cap.release()
    cv2.destroyAllWindows()


def start_processing():
    # --- Ejecutar la Deteccion de mano en un hilo separado.
    t = threading.Thread(target=hand_state, daemon=True)
    t.start()

#--------------------------------------------------------------------------
#---------------------------  FIN DEL PROGRAMA ----------------------------
#--------------------------------------------------------------------------
