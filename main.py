#--------------------------------------------------------------------------
#------- HIGHEST GEAR ----------------------------------------------
#------- Procesamiento de mano por camara-------------------------------------------
#------- Por: Daniel Perez    daniel.perez19@udea.edu.co --------------
#-------      Edisson Chamorro    john.chamorro@udea.edu.co -----------------
#-------      Estudiantes Departamento Electrónica y Telecomunicaciones -------------------
#------- Curso B�sico de Procesamiento de Im�genes y Visi�n Artificial-----
#-------  Octubre de 2025--------------------------------------------------
#--------------------------------------------------------------------------

import pygame
import os
from processing import start_processing, state, position
from game import Game


def main():
    
    pygame.init()
    pygame.mixer.init()

    # Configuración de ventana
    WIDTH, HEIGHT = 1000, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Exidium 🚗")

    # Reproducir música de fondo
    music_path = os.path.join("assets", "song.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # repetir siempre
    
    # Iniciar hilo para procesamiento de cámara
    start_processing()
    
    # Crear instancia del juego
    game = Game(screen, WIDTH, HEIGHT, assets_path="assets", state=state, position=position)

    # Loop principal.
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                 running = False

        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(60)
     

    pygame.quit()


if __name__ == "__main__":
    main()
