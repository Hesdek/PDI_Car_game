import pygame
import os
import processing
import threading
from game import Game

def main():
    global state, position
    
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
    hilo_hand_state = threading.Thread(target=processing.hand_state, daemon=True)
    hilo_hand_state.start()
    # Crear instancia del juego
    game = Game(screen, WIDTH, HEIGHT)

    # Loop principal
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
