import cv2
from ultralytics import YOLO

# Cargar modelo entrenado
model = YOLO("runs/detect/train/weights/best.pt")   # Ajusta la ruta si es distinta

# Ruta del video a analizar
VIDEO_PATH = "video.mp4"   # Cambia por el video que quieras

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Error al abrir el video.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Inferencia con YOLO
    results = model(frame)[0]

    # Dibujar detecciones
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls = int(box.cls[0])
        conf = float(box.conf[0])

        # Nombre de la clase
        label = f"{model.names[cls]} {conf:.2f}"

        # Rectángulo
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Texto
        cv2.putText(
            frame,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    # Mostrar resultado
    cv2.imshow("Detección de señales", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
