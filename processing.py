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

        # Create a blank mask and draw filtered contours on it
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)  # máscara de 1 canal (grayscale)
        filtered_contours = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000 and area < 30000:  # Mano cerrada
                filtered_contours.append(contour)
                estado_mano = "Mano CERRADA"
                color_estado = (0, 0, 255)  # Rojo
            elif area > 30000:  # Mano abierta
                filtered_contours.append(contour)
                estado_mano = "Mano ABIERTA"
                color_estado = (0, 255, 0)  # Verde

        cv2.drawContours(mask, filtered_contours, -1, (255), cv2.FILLED)
        
        # Aplicar mascara a la imagen original opcional
        # masked_img = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Mostrar el estado en la imagen principal
        cv2.putText(frame, estado_mano, (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color_estado, 2, cv2.LINE_AA)
        
        # También mostrar el área si hay contornos detectados
        if filtered_contours:
            area_actual = cv2.contourArea(filtered_contours[0])
            cv2.putText(frame, f"Area: {area_actual:.0f}", (50, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_estado, 2, cv2.LINE_AA)
            
        # Mostrar ventanas
        cv2.imshow("Deteccion de Mano", frame)
        # cv2.imshow("Mascara", masked_img)

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    return area

