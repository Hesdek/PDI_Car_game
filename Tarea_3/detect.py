import cv2
import numpy as np
from ultralytics import YOLO

# ======================
#   CARGAR MODELO YOLO
# ======================
model = YOLO("best.pt")

# ======================
#   VIDEO
# ======================
cap = cv2.VideoCapture("dataset/test/videos/video3.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ======================
    #   PREDICCIÓN SOBRE FRAME COMPLETO
    # ======================
    results = model(frame, verbose=False)

    # Iterar detecciones
    for r in results:
        for box in r.boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])
            nombre = model.names[cls]

            # Ignorar detecciones débiles
            if conf < 0.50:
                continue

            # Coordenadas
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # ======================
            #   DIBUJAR RECUADRO VERDE
            # ======================
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

            # Nombre arriba del recuadro
            cv2.putText(frame, f"{nombre} ({conf:.2f})",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

            # ======================
            #   IMPRIMIR EN CONSOLA
            # ======================
            |#print(f"Señal detectada: {nombre} — Confianza: {conf:.2f}")

    # ======================
    #   MOSTRAR FRAME
    # ======================
    cv2.imshow("Video - YOLO deteccion", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
