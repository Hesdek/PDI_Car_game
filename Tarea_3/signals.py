from ultralytics import YOLO

def main():
    # Cargar modelo (puede ser yolov8n.pt o el que tú quieras)
    model = YOLO("best.pt")

    # Entrenar
    model.train(
        data="data.yaml",   # YAML generado automáticamente
        epochs=100,
        imgsz=640,
        batch=16
        #cpu=0  # usa GPU si tienes, si no, cámbialo a 'cpu'
    )

    # Evaluación automática
    model.val()

    # Prueba rápida con imágenes del test
    results = model.predict("dataset/test/images", save=True)
    print("Listo. Resultados guardados en runs/detect/predict/")

if __name__ == "__main__":
    main()
