import pygame
import os
from utils import load_image

class Player:
    def __init__(self, screen, width, height, assets_path="assets"):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height

        # dimensiones del sprite (puedes ajustar)
        self.PW, self.PH = 160, 90

        # cargar sprite (fallback a rect)
        self.img = load_image(os.path.join(assets_path, "car.png"), (self.PW, self.PH)) if True else None
        self.x = width // 2 - self.PW // 2
        self.y = height - self.PH - 28
        self.speed = 5

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        # limites (dejamos holgura)
        min_x = 120
        max_x = self.WIDTH - 120 - self.PW
        self.x = max(min_x, min(max_x, self.x))

    def update(self, dt):
        # por ahora la lógica de movimiento ya la hace handle_input()
        pass

    def draw(self):
        if self.img:
            self.screen.blit(self.img, (self.x, self.y))
        else:
            # fallback simple
            pygame.draw.rect(self.screen, (120, 10, 10), (self.x, self.y, self.PW, self.PH))
            pygame.draw.circle(self.screen, (0,0,0), (self.x + 30, self.y + self.PH - 8), 10)
            pygame.draw.circle(self.screen, (0,0,0), (self.x + self.PW - 30, self.y + self.PH - 8), 10)
