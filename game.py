import pygame
from settings import WIDTH, HEIGHT, FPS
from assets import screen, soundtrack, tires, crash
from ui import show_score, show_message
from player.py import Player
from enemy import Truck
from background import Background

def game_loop():
    clock = pygame.time.Clock()

    # Objetos
    player = Player()
    bg = Background(speed=4)
    truck = Truck(speed=6)

    score = 0
    soundtrack.play(-1)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.x_change = -6
                if event.key == pygame.K_RIGHT:
                    player.x_change = 6
                if event.key == pygame.K_UP:
                    bg.speed += 1
                if event.key == pygame.K_DOWN and bg.speed > 2:
                    bg.speed -= 1
                truck.speed = bg.speed + 2

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    player.x_change = 0

        # --- Actualizar ---
        player.move()
        bg.update()
        truck.update()

        if truck.y > HEIGHT:
            truck.reset(bg.speed + 2)
            score += 1

        # --- Colisiones ---
        if player.get_rect().colliderect(truck.get_rect()):
            crash.play()
            show_message("¡Chocaste con un camión!")
            return  # salir del bucle y reiniciar

        if player.x < 35 or player.x > WIDTH - 87:
            tires.play()
            crash.play()
            show_message("¡Te saliste de la carretera!")
            return

        # --- Dibujar ---
        bg.draw(screen)
        truck.draw(screen)
        player.draw(screen)
        show_score(score)

        pygame.display.flip()
