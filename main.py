# main.py
import pygame
from game import Game

def main():
    pygame.init()
    WIDTH, HEIGHT = 1000, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Exidium 🚗")

    game = Game(screen, WIDTH, HEIGHT, assets_path="assets")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update()
        game.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
