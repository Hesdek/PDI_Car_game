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


white_low  = np.array([0, 0, 200])
white_high = np.array([180, 40, 255])
# ======================
#   DETECTOR DE FORMAS
# ======================
def detectar_forma(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.03 * peri, True)

    if len(approx) >8:
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
     # Rojo
    mask_r1 = cv2.inRange(hsv, red_low1, red_high1)
    mask_r2 = cv2.inRange(hsv, red_low2, red_high2)
    mask_red = cv2.bitwise_or(mask_r1, mask_r2)

    # Blanco
    mask_white = cv2.inRange(hsv, white_low, white_high)

    # Señales reglamentarias → rojo borde + blanco centro
    mask_total = cv2.bitwise_or(mask_red, mask_white)
   
    # ---- LIMPIEZA ----
    kernel = np.ones((5,5), np.uint8)
    mask_clean = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

    # ---- CONTORNOS ----
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 100:
            continue

        forma = detectar_forma(cnt)
        if forma not in ["circulo"]:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        roi_color = frame[y:y+100, x:x+100]

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

                # <<< AQUI IMPRIMIMOS >>>
                print(f"Señal detectada: {nombre} — Confianza: {conf:.2f}")

                # Dibujar bbox
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(frame, f"{nombre} {conf:.2f}", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow("Señal segmentada", roi_color)

    cv2.imshow("Frame original", frame)
    cv2.imshow("Mascara segmentacion", mask_clean)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
