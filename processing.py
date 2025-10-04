import cv2
import numpy as np

def detectar_estado_mano():
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
        limite_inferior_verde = np.array([35, 100, 30])
        limite_superior_verde = np.array([100, 255, 255])
        
        # Crear máscara para verde
        mascara_verde = cv2.inRange(image_hsv, limite_inferior_verde, limite_superior_verde)

        # Convertir mascara a uint8
        S_uint8 = (mascara_verde * 255).astype(np.uint8)

        # Encontrar objetos (contornos)
        contours, _ = cv2.findContours(S_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Variables para determinar estado de la mano
        estado_mano = "No detectada"
        color_estado = (0, 0, 255)  # Rojo por defecto
        area = 0  # Inicializar área
        posicion_mano = "Centro"
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
                    posicion_mano = "Izquierda"
                elif centro_x > tercio_derecho:
                    posicion_mano = "Derecha"

                
                # Dibujar punto central
                cv2.circle(frame, (centro_x, centro_y), 8, (255, 0, 0), -1)
                
                # Dibujar líneas divisorias
                cv2.line(frame, (tercio_izquierdo, 0), (tercio_izquierdo, frame.shape[0]), (255, 255, 0), 2)
                
                cv2.line(frame, (tercio_derecho, 0), (tercio_derecho, frame.shape[0]), (255, 255, 0), 2)
            
            # Determinar estado de la mano (abierta/cerrada)
            if 10000 < area < 10000:
                estado_mano = "Mano CERRADA"
            elif area >= 10000:
                estado_mano = "Mano ABIERTA"

        # Mostrar información
        color_estado = (0, 255, 0) if estado_mano == "Mano ABIERTA" else (0, 0, 255)
        color_posicion = (255, 255, 0)  # Azul claro para posición
        cv2.drawContours(mask, filtered_contours, -1, (255), cv2.FILLED)
        
        # Aplicar mascara a la imagen original opcional
        # masked_img = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Información del estado de la mano
        cv2.putText(frame, f"Estado: {estado_mano}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color_estado, 2)
        cv2.putText(frame, f"Area: {area:.0f}", (50, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_estado, 2)
        
        # Información de la posición
        cv2.putText(frame, f"Posicion: {posicion_mano}", (50, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color_posicion, 2)
        cv2.putText(frame, f"Centro X: {centro_x}", (50, 170), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_posicion, 2)
        
        # Mostrar coordenadas en la parte superior derecha
        cv2.putText(frame, f"Frame: {frame.shape[1]}x{frame.shape[0]}", 
                   (frame.shape[1] - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow("Deteccion de Mano", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return area, posicion_mano

