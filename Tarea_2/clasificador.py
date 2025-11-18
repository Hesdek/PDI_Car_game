from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

class ClasificadorSenalesColor:
    def __init__(self, ruta_modelo, clases):
        self.model = load_model(ruta_modelo)
        self.class_names = clases

    def preparar_imagen(self, ruta_img):
        # Cargar imagen a color y redimensionar a 28x28
        img = image.load_img(ruta_img, color_mode="rgb", target_size=(28, 28))
        img_array = image.img_to_array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)  # shape (1, 28, 28, 3)
        return img_array

    def predecir(self, ruta_img):
        img_preparada = self.preparar_imagen(ruta_img)
        pred = self.model.predict(img_preparada)
        indice = np.argmax(pred)
        clase = self.class_names[indice]
        confianza = float(np.max(pred))
        return clase, confianza
