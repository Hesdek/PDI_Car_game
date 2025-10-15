import cv2
import numpy as np
import threading

state = {"value":"No detectada"}
position = {"value":"Centro"}

def hand_state():
    global state, position
    # Abrir cámara
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Voltear imagen (efecto espejo)
        frame = cv2.flip(frame, 1)

        # Convertir a HSV
        image_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Cambié RGB2HSV por BGR2HSV
        
        # Rango para VERDE https://www.selecolor.com/en/hsv-color-picker/
        limite_inferior = np.array([35, 100, 30])
        limite_superior = np.array([100, 255, 255])
        
        # Crear máscara para verde
        mascara_verde = cv2.inRange(image_hsv, limite_inferior, limite_superior)

        # Convertir mascara a uint8
        S_uint8 = (mascara_verde * 255).astype(np.uint8)

        # Encontrar objetos (contornos)
        contours, _ = cv2.findContours(S_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Variables para determinar estado de la mano
        color_estado = (0, 0, 255)  # Rojo por defecto
        area = 0  # Inicializar área
        centro_x = 0

        # Create a blank mask and draw filtered contours on it
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)  # máscara de 1 canal (grayscale)
        filtered_contours = []
        
        if contours:
            # Tomar el contorno más grande
            contorno_principal = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(contorno_principal)
            
            # Calcular el centro del contorno
            M = cv2.moments(contorno_principal)
            if M["m00"] != 0:
                centro_x = int(M["m10"] / M["m00"])
                centro_y = int(M["m01"] / M["m00"])
                
                # Determinar posición izquierda/derecha
                ancho_frame = frame.shape[1]
                tercio_izquierdo = ancho_frame // 3
                tercio_derecho = 2 * ancho_frame // 3
                
                if centro_x < tercio_izquierdo:
                    position["value"] = "Izquierda"
                elif centro_x > tercio_derecho:
                    position["value"] = "Derecha"

                
                # Dibujar punto central
                cv2.circle(frame, (centro_x, centro_y), 8, (255, 0, 0), -1)
                
                # Dibujar líneas divisorias
               # cv2.line(frame, (tercio_izquierdo, 0), (tercio_izquierdo, frame.shape[0]), (255, 255, 0), 2)
                
               # cv2.line(frame, (tercio_derecho, 0), (tercio_derecho, frame.shape[0]), (255, 255, 0), 2)
            
            # Determinar estado de la mano (abierta/cerrada)
            if  area < 20000:
                state["value"] = "CERRADA"
            elif area >= 20000:
                state["value"] = "ABIERTA"

        # Mostrar información
        color_estado = (0, 255, 0) if state == "Mano Abierta" else (0, 0, 255)
        color_posicion = (255, 255, 0)  # Azul claro para posición
        cv2.drawContours(mask, filtered_contours, -1, (255), cv2.FILLED)
        
        # Información del estado de la mano
        cv2.putText(frame, f"Estado: {state}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color_estado, 2)
        
        # Información de la posición
        cv2.putText(frame, f"Posicion: {position}", (50, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color_posicion, 2)
       
        # Mostrar coordenadas en la parte superior derecha
        cv2.putText(frame, f"Frame: {frame.shape[1]}x{frame.shape[0]}", 
                   (frame.shape[1] - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow("Deteccion de Mano", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    

def start_processing():
    # Inicia el hilo en paralelo
    t = threading.Thread(target=hand_state, daemon=True)
    t.start()