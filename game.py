#--------------------------------------------------------------------------
#------- HIGHEST GEAR ----------------------------------------------
#------- Procesamiento de mano por camara-------------------------------------------
#------- Por: Daniel Perez    daniel.perez19@udea.edu.co --------------
#-------      Edisson Chamorro    john.chamorro@udea.edu.co -----------------
#-------      Estudiantes Departamento Electrónica y Telecomunicaciones -------------------
#------- Curso B�sico de Procesamiento de Im�genes y Visi�n Artificial-----
#-------  Octubre de 2025--------------------------------------------------
#-
import pygame
from scene import Scene
from player import Player

class Game:
    def __init__(self, screen, width, height, assets_path="assets", state=None, position=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.position = position
        self.scene = Scene(screen, width, height, assets_path=assets_path, state=state)
        self.player = Player(screen, width, height, assets_path=assets_path, position=position)
        self.clock = pygame.time.Clock()
        self.FPS = 60

    def update(self):
        dt = self.clock.tick(self.FPS) / 1000.0
        # input & player movement        
        self.player.handle_input(dt)
        self.player.update(dt)
        # actualizar escena (scroll + fases)
        self.scene.update(dt)

    def draw(self):
        # scene dibuja la carretera y la ciudad
        self.scene.draw(player_offset=self.player.offset)
        # dibujar el carro encima (fijo en centro)
        self.player.draw()
