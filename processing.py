import cv2
import numpy as np

def camera_processing():
    # Abrir cámara
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
    if not ret:
        break

    # Voltear imagen (efecto espejo)
    frame = cv2.flip(frame, 1)

    # Convertir a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Rango de piel (ajustar según tu tono y luz)
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    # Crear máscara
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Suavizar máscara
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Buscar contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Tomar contorno más grande (mano)
        c = max(contours, key=cv2.contourArea)

        # Dibujar contorno
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)

        # Convex hull
        hull = cv2.convexHull(c)
        cv2.drawContours(frame, [hull], -1, (0, 0, 255), 2)

        # Defectos de convexidad
        hull_indices = cv2.convexHull(c, returnPoints=False)
        if len(hull_indices) > 3:
            defects = cv2.convexityDefects(c, hull_indices)
            if defects is not None:
                count_defects = 0
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(c[s][0])
                    end = tuple(c[e][0])
                    far = tuple(c[f][0])

                    # Geometría para contar dedos
                    a = np.linalg.norm(np.array(end) - np.array(start))
                    b = np.linalg.norm(np.array(far) - np.array(start))
                    c_len = np.linalg.norm(np.array(end) - np.array(far))
                    angle = np.arccos((b**2 + c_len**2 - a**2) / (2*b*c_len))

                    if angle <= np.pi/2:  # Ángulo menor a 90° => dedo extendido
                        count_defects += 1
                        cv2.circle(frame, far, 5, (255, 0, 0), -1)

                # Dedos extendidos ≈ defectos + 1
                dedos = count_defects + 1

                # Estado de la mano
                if dedos >= 4:
                    estado = "Abierta"
                else:
                    estado = "Cerrada"

                # Posición horizontal (izq, der, centro)
                x, y, w, h = cv2.boundingRect(c)
                cx = x + w // 2
                if cx < frame.shape[1] // 3:
                    posicion = "Izquierda"
                elif cx > 2 * frame.shape[1] // 3:
                    posicion = "Derecha"
                else:
                    posicion = "Centro"

                print(f"Mano {estado}, posicion {posicion}")

                # Mostrar texto en pantalla
                cv2.putText(frame, f"{estado} - {posicion}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Mostrar ventanas
    cv2.imshow("Deteccion de Mano", frame)
    cv2.imshow("Mascara", mask)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cap.release()
    cv2.destroyAllWindows()