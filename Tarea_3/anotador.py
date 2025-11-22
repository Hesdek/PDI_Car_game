import cv2
import os

# ================================
# CONFIGURACIÓN
# ================================
IMAGES_DIR = "dataset/train/images"      # Carpeta de imágenes
OUTPUT_DIR = "dataset/train/labels"      # Carpeta donde se guardan los .txt
# ================================

drawing = False
ix, iy = -1, -1
boxes = []
current_class = 0
current_image = None
image_name = ""

# Crear carpeta labels si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_bbox(event, x, y, flags, param):
    global ix, iy, drawing, current_image, boxes, current_class

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        img_copy = current_image.copy()
        cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        text = f"class {current_class}"
        cv2.putText(img_copy, text, (ix, iy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        cv2.imshow("Anotador", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(current_image, (ix, iy), (x, y), (0, 255, 0), 2)
        boxes.append((current_class, ix, iy, x, y))
        cv2.imshow("Anotador", current_image)


def guardar_labels(img_name, img, boxes):
    h, w = img.shape[:2]
    label_path = os.path.join(OUTPUT_DIR, img_name.rsplit(".",1)[0] + ".txt")

    with open(label_path, "w") as f:
        for cls, x1, y1, x2, y2 in boxes:

            # Convertir las coordenadas a YOLO (normalizado)
            x_center = ((x1 + x2) / 2) / w
            y_center = ((y1 + y2) / 2) / h
            box_w = abs(x2 - x1) / w
            box_h = abs(y2 - y1) / h
            if "pare" in image_name:
                clase=0
            elif "velocidad" in image_name:
                clase=1
            elif "izquierda" in image_name:
                clase=2
            elif "derecha" in image_name:
                clase=3
            elif "parada" in image_name:
                clase=4
            f.write(f"{clase} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}\n")

    print(f"✔ Labels guardados en {label_path}")


def main():
    global current_image, image_name, boxes, current_class

    # Listar imágenes
    image_files = [f for f in os.listdir(IMAGES_DIR)
                   if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    if not image_files:
        print("❌ No hay imágenes en la carpeta.")
        return

    idx = 0

    while idx < len(image_files):
        image_name = image_files[idx]
        current_image = cv2.imread(os.path.join(IMAGES_DIR, image_name))
        boxes = []

        cv2.namedWindow("Anotador")
        cv2.setMouseCallback("Anotador", draw_bbox)

        print(f"\n🖼 Anotando: {image_name}")
        cv2.imshow("Anotador", current_image)

        while True:
            key = cv2.waitKey(1) & 0xFF

            # Guardar labels con ENTER
            if key == 13:
                guardar_labels(image_name, current_image, boxes)
                break

            # Siguiente imagen
            elif key == ord('n'):
                break

            # Salir con ESC
            elif key == 27:
                cv2.destroyAllWindows()
                return

        idx += 1

    print("\n✔ ¡Todas las imágenes fueron anotadas!")
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
