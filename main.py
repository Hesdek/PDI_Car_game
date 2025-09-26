import pygame
from game import Game

def main():
    pygame.init()
    
    # Configuración de ventana
    WIDTH, HEIGHT = 1000, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Exidium 🚗")

    # Crear instancia del juego
    game = Game(screen, WIDTH, HEIGHT)

    # Loop principal
    running = True
    clock = pygame.time.Clock()

    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Actualizar lógica del juego
        game.update()

        # Dibujar en pantalla
        game.draw()

        # Refrescar
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()


if __name__ == "__main__":
    main()
