import cv2
import numpy as np
import threading

# Variables globales para el estado y posición de la mano
state = {"value": "No detectada"}   # Puede ser: No detectada, Abierta, Cerrada
position = {"value": "Centro"}      # Puede ser: Izquierda, Centro, Derecha


def hand_state():
    global state, position

    # --- ABRIR CÁMARA ---
    cap = cv2.VideoCapture(0)

    # Verificar que la cámara esté disponible
    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # --- VOLTEAR IMAGEN (efecto espejo) ---
        frame = cv2.flip(frame, 1)

        # --- CONVERTIR A ESPACIO DE COLOR HSV ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # --- RANGO DE COLOR PARA PIEL (ajustable según iluminación) ---
        # Estos valores filtran tonos de piel típicos
        lower_skin = np.array([0, 30, 60], dtype=np.uint8)
        upper_skin = np.array([20, 150, 255], dtype=np.uint8)

        # --- CREAR MÁSCARA PARA COLOR DE PIEL ---
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # --- APLICAR FILTROS MORFOLÓGICOS PARA REDUCIR RUIDO ---
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        mask = cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=2)
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)

        # --- ENCONTRAR CONTORNOS ---
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Si no hay contornos, no hay mano detectada
        if len(contours) == 0:
            state["value"] = "No detectada"
            position["value"] = "Centro"
            cv2.imshow("Detección de Mano", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # --- SELECCIONAR EL CONTORNO MÁS GRANDE (la mano) ---
        contour = max(contours, key=cv2.contourArea)

        # --- FILTRAR OBJETOS MUY PEQUEÑOS O MUY GRANDES ---
        area = cv2.contourArea(contour)
        if area < 3000 or area > 100000:
            state["value"] = "No detectada"
            position["value"] = "Centro"
            cv2.imshow("Detección de Mano", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # --- DIBUJAR CONTORNO PRINCIPAL ---
        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

        # --- CALCULAR EL CENTRO DE LA MANO ---
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cx, cy), 7, (255, 0, 0), -1)
        else:
            cx, cy = 0, 0

        # --- DETERMINAR POSICIÓN DE LA MANO ---
        width = frame.shape[1]
        left = width // 3
        right = 2 * width // 3

        if cx < left:
            position["value"] = "Izquierda"
        elif cx > right:
            position["value"] = "Derecha"
        else:
            position["value"] = "Centro"

        # --- CALCULAR LA FORMA CONVEXA Y DEFECTOS (dedos) ---
        hull = cv2.convexHull(contour, returnPoints=False)
        if hull is not None and len(hull) > 3:
            defects = cv2.convexityDefects(contour, hull)

            if defects is not None:
                count_defects = 0

                # Recorremos los defectos convexos (hendiduras entre los dedos)
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(contour[s][0])
                    end = tuple(contour[e][0])
                    far = tuple(contour[f][0])

                    # Calcular los lados del triángulo formado por los puntos del defecto
                    a = np.linalg.norm(np.array(end) - np.array(start))
                    b = np.linalg.norm(np.array(far) - np.array(start))
                    c = np.linalg.norm(np.array(end) - np.array(far))

                    # Calcular el ángulo del defecto
                    angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))

                    # Si el ángulo es menor a 90 grados, probablemente es un dedo
                    if angle <= np.pi / 2:
                        count_defects += 1
                        cv2.circle(frame, far, 5, (0, 0, 255), -1)

                # --- CLASIFICAR ESTADO DE LA MANO ---
                # Si hay muchos defectos => mano abierta, pocos => cerrada
                if count_defects >= 3:
                    state["value"] = "ABIERTA"
                else:
                    state["value"] = "CERRADA"
            else:
                state["value"] = "CERRADA"

        # --- MOSTRAR INFORMACIÓN EN PANTALLA ---
        cv2.putText(frame, f"Estado: {state['value']}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.putText(frame, f"Posicion: {position['value']}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Detección de Mano", frame)

        # --- SALIR CON LA TECLA 'q' ---
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # --- LIBERAR RECURSOS ---
    cap.release()
    cv2.destroyAllWindows()


def start_processing():
    """Ejecuta la detección de mano en un hilo separado."""
    t = threading.Thread(target=hand_state, daemon=True)
    t.start()
