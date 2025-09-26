# game.py
import pygame
from scene import Scene
from player import Player

class Game:
    def __init__(self, screen, width, height, assets_path="assets"):
        self.screen = screen
        self.width = width
        self.height = height
        self.scene = Scene(screen, width, height, assets_path=assets_path)
        self.player = Player(screen, width, height, assets_path=assets_path)
        self.clock = pygame.time.Clock()
        self.FPS = 60

    def update(self):
        dt = self.clock.tick(self.FPS) / 1000.0
        # input & player movement
        self.player.handle_input()
        self.player.update(dt)
        # actualizar escena (scroll + fases)
        self.scene.update(dt)

    def draw(self):
        # scene dibuja la carretera y la ciudad
        self.scene.draw(player_x=self.player.x)
        # dibujar el carro encima
        self.player.draw()
