from clasificador import ClasificadorSenalesColor

if __name__ == "__main__":
    clases = ['PARE', 'CEDA_EL_PASO', 'PROHIBIDO_PASAR', 'VELOCIDAD', 'GIRO']
    clasificador = ClasificadorSenalesColor("modelo_senales_color.h5", clases)

    ruta = "prueba_pare.jpg"
    clase, confianza = clasificador.predecir(ruta)
    print(f"La imagen pertenece a: {clase} (confianza: {confianza:.2f})")
