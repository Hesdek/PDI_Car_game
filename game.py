import pygame
import os
import sys

pygame.init()

# Configuración de ventana
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colores
SKY_COLOR = (0, 0, 50)
GRASS_COLOR = (0, 120, 0)
ROAD_COLOR = (100, 100, 100)
BORDER_COLORS = [(255, 0, 0), (255, 255, 255)]  # rojo y blanco

# FPS
clock = pygame.time.Clock()
FPS = 60

# Assets
assets_path = "assets"
city_img = pygame.image.load(os.path.join(assets_path, "city.png"))
city_img = pygame.transform.scale(city_img, (WIDTH, 300))

player_img = pygame.image.load(os.path.join(assets_path, "car.png"))
PLAYER_WIDTH, PLAYER_HEIGHT = 160, 90
player_img = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))

# Posición inicial del carro
player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - PLAYER_HEIGHT - 20
player_speed = 7

# Segmentos de carretera
NUM_SEGMENTS = 30
segment_height = HEIGHT // NUM_SEGMENTS
road_segments = []

for i in range(NUM_SEGMENTS):
    road_segments.append({
        "y": i * segment_height,
        "color": BORDER_COLORS[i % 2]
    })

scroll = 0
road_speed = 5  # velocidad carretera


def draw_scene():
    global scroll, player_x

    # Fondo cielo
    screen.fill(SKY_COLOR)

    # Ciudad
    screen.blit(city_img, (0, 50))

    # Pasto
    pygame.draw.rect(screen, GRASS_COLOR, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    # Dibujar carretera
    for i, seg in enumerate(road_segments):
        # Calcular "perspectiva" escalando ancho
        perspective = 1 - (i / NUM_SEGMENTS)  # AHORA se invierte la escala
        road_w = int(WIDTH * perspective * 0.8)
        x1 = WIDTH // 2 - road_w // 2
        x2 = WIDTH // 2 + road_w // 2
        y = HEIGHT - i * segment_height + scroll

        if HEIGHT // 2 < y < HEIGHT:  # dibujar solo en parte baja
            # carretera
            pygame.draw.polygon(screen, ROAD_COLOR,
                                [(x1, y), (x2, y),
                                 (x2 + 20, y + segment_height),
                                 (x1 - 20, y + segment_height)])

            # bordes
            pygame.draw.polygon(screen, seg["color"],
                                [(x1 - 20, y), (x1, y),
                                 (x1, y + segment_height),
                                 (x1 - 20, y + segment_height)])
            pygame.draw.polygon(screen, seg["color"],
                                [(x2, y), (x2 + 20, y),
                                 (x2 + 20, y + segment_height),
                                 (x2, y + segment_height)])

    # Carro (con movimiento horizontal)
    screen.blit(player_img, (player_x, player_y))


def update_segments():
    global scroll, road_segments
    scroll += road_speed
    if scroll >= segment_height:
        scroll = 0
        road_segments.append(road_segments.pop(0))  # reciclar segmento


# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Controles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # Limitar movimiento en pantalla
    if player_x < 100:
        player_x = 100
    if player_x > WIDTH - 100 - PLAYER_WIDTH:
        player_x = WIDTH - 100 - PLAYER_WIDTH

    update_segments()
    draw_scene()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
