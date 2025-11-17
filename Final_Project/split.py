import os
import random
import shutil

# Rutas base
BASE = "Final_Project/dataset"  # Ajusta si tu ruta es diferente
IMG_DIR = os.path.join(BASE, "images")
LBL_DIR = os.path.join(BASE, "labels")

# Porcentajes del split
TRAIN_SPLIT = 0.7
VAL_SPLIT = 0.2
TEST_SPLIT = 0.1

# Crear carpetas destino
for carpeta in ["train/images", "train/labels",
                "val/images", "val/labels",
                "test/images", "test/labels"]:
    os.makedirs(os.path.join(BASE, carpeta), exist_ok=True)

# Listar imágenes válidas
imagenes = [f for f in os.listdir(IMG_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))]

# Mezclar
random.shuffle(imagenes)

# Cálculo de cortes
n = len(imagenes)
n_train = int(n * TRAIN_SPLIT)
n_val = int(n * VAL_SPLIT)

train_imgs = imagenes[:n_train]
val_imgs = imagenes[n_train : n_train + n_val]
test_imgs = imagenes[n_train + n_val :]

def mover(lista, destino):
    for img in lista:
        # nombre base sin extensión
        nombre_base = os.path.splitext(img)[0]

        # nombre del label correspondiente
        lbl = nombre_base + ".txt"

        # rutas completas
        src_img = os.path.join(IMG_DIR, img)
        src_lbl = os.path.join(LBL_DIR, lbl)

        dst_img = os.path.join(BASE, destino, "images", img)
        dst_lbl = os.path.join(BASE, destino, "labels", lbl)

        # mover imagen
        shutil.copy(src_img, dst_img)

        # mover label si existe
        if os.path.exists(src_lbl):
            shutil.copy(src_lbl, dst_lbl)
        else:
            print(f"[WARN] No existe label para {img}. Se omite label.")

# Mover archivos
mover(train_imgs, "train")
mover(val_imgs, "val")
mover(test_imgs, "test")

print("Split completado.")
print(f"Train: {len(train_imgs)}, Val: {len(val_imgs)}, Test: {len(test_imgs)}")
