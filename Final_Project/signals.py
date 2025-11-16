from ultralytics import YOLO
import cv2

model = YOLO("best.pt")

cap = cv2.VideoCapture("video.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)

    annotated = results[0].plot()   # dibuja cajas y labels
    cv2.imshow("Detección", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
