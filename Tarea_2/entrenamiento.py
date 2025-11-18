import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

IMG_SIZE = (28, 28)
BATCH_SIZE = 8

# Cargar dataset (carpetas por clase)
train_ds = tf.keras.utils.image_dataset_from_directory(
    "dataset",
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    color_mode="rgb",   
    batch_size=BATCH_SIZE
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    "dataset",
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    color_mode="rgb",
    batch_size=BATCH_SIZE
)

# Clases
class_names = train_ds.class_names
print("Clases detectadas:", class_names)

# Normalización 0–1
normalization_layer = layers.Rescaling(1./255)
train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))


# --- Definición de modelo CNN ---
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(28, 28, 3)),  # 3 canales
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.4),
    layers.Dense(len(class_names), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

history = model.fit(train_ds, validation_data=val_ds, epochs=30)

# Guardar el modelo
model.save("modelo_senales_color.h5")
print("✅ Modelo guardado correctamente como 'modelo_senales_color.h5'")
