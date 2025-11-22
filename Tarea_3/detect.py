import cv2
import numpy as np
from ultralytics import YOLO

# ======================
#   CARGAR MODELO YOLO
# ======================
model = YOLO("best.pt")

# ======================
#   RANGOS HSV
# ======================

red_low1  = np.array([0, 150, 80])
red_high1 = np.array([10, 255, 255])

red_low2  = np.array([170, 150, 80])
red_high2 = np.array([180, 255, 255])


# ======================
#   DETECTOR DE FORMAS
# ======================
def detectar_forma(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.03 * peri, True)

    if len(approx) > 8:
        return "circulo"
    return "otro"

# ======================
#   VIDEO
# ======================
cap = cv2.VideoCapture("dataset/test/videos/video3.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # ---- MÁSCARAS ----

    mask_r1 = cv2.inRange(hsv, red_low1, red_high1)
    mask_r2 = cv2.inRange(hsv, red_low2, red_high2)
    mask_red = cv2.bitwise_or(mask_r1, mask_r2)
  

    mask_total = mask_red
   

    # ---- LIMPIEZA ----
    kernel = np.ones((5,5), np.uint8)
    mask_clean = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

    # ---- CONTORNOS ----
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue

        forma = detectar_forma(cnt)
        if forma not in ["circulo", "rombo"]:
            continue

        # ---- ROI EN MASCARA ----
        x, y, w, h = cv2.boundingRect(cnt)

        # ---- ROI EN IMAGEN ORIGINAL (IMPORTANTÍSIMO) ----
        roi_color = frame[y:y+h, x:x+w]

        # evitar errores si ROI sale muy pequeño
        if roi_color.size == 0:
            continue

        # ======================
        #    PREDICCIÓN YOLO
        # ======================
        results = model(roi_color, verbose=False)

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                nombre = model.names[cls]

                # Dibujar bbox en frame completo
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(frame, f"{nombre} {conf:.2f}", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # Mostrar señal segmentada (ROI procesada)
        cv2.imshow("Señal segmentada", roi_color)

    # Ventanas principales
    cv2.imshow("Frame original", frame)
    cv2.imshow("Mascara segmentacion", mask_clean)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
