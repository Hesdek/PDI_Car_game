import pygame
import os
from utils import load_image

class Player:
    def __init__(self, screen, width, height, assets_path="assets"):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height

        # dimensiones del sprite
        self.PW, self.PH = 160, 90
        self.img = load_image(os.path.join(assets_path, "car.png"), (self.PW, self.PH)) if True else None

        # offset lateral normalizado [-1..1]. 0 = centro de la pantalla.
        self.offset = 0.0
        self.max_offset = 1.0
        # velocidad de giro (unidades offset por segundo)
        self.steer_speed = 2.5
        # suavizado (inercia)
        self.steer_damping = 8.0
        self.target_offset = 0.0

        # posicion vertical fija (se dibuja siempre en centro abajo)
        self.y = height - self.PH - 28

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        steer = 0.0
        if keys[pygame.K_LEFT]:
            steer -= 1.0
        if keys[pygame.K_RIGHT]:
            steer += 1.0

        # actualizar target_offset
        self.target_offset += steer * self.steer_speed * dt
        # clamp target
        self.target_offset = max(-self.max_offset, min(self.max_offset, self.target_offset))

    def update(self, dt):
        # suavizar towards target_offset (simple damping)
        diff = self.target_offset - self.offset
        self.offset += diff * min(1.0, self.steer_damping * dt)
        # opcional: frenar el target (vuelve al centro si no hay input)
        # self.target_offset *= (1.0 - min(1.0, 3.0*dt))

    def draw(self):
        # dibujar el coche centrado horizontalmente en pantalla
        x = self.WIDTH // 2 - self.PW // 2
        if self.img:
            self.screen.blit(self.img, (x, self.y))
        else:
            pygame.draw.rect(self.screen, (120, 10, 10), (x, self.y, self.PW, self.PH))
            pygame.draw.circle(self.screen, (0,0,0), (x + 30, self.y + self.PH - 8), 10)
            pygame.draw.circle(self.screen, (0,0,0), (x + self.PW - 30, self.y + self.PH - 8), 10)
