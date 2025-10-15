# scene.py
import pygame
import pygame.gfxdraw as gfx
import os
import math
from utils import blend_color, draw_aaline, load_image
from track import Track
from minimap import Minimap

def make_fog_surf(width, fog_height, sky_color):
    """
    Genera y retorna una Surface con degradado de niebla (alpha) del ancho dado.
    """
    small_w = 200
    small_fog = pygame.Surface((small_w, fog_height), pygame.SRCALPHA)
    for r in range(fog_height):
        t = r / max(1, fog_height - 1)
        alpha = int(180 * (t ** 1.4))
        gfx.box(small_fog, (0, r, small_w, 1), (sky_color[0], sky_color[1], sky_color[2], alpha))
    return pygame.transform.smoothscale(small_fog, (width, fog_height)).convert_alpha()

class Scene:
    def __init__(self, screen, width, height, assets_path="assets", state=None):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height
        self.assets_path = assets_path
        self.state = state if state is not None else {"value": "No detectada"}


        # Cargar sprites del coche
        self.car_sprite = load_image(os.path.join(assets_path, "car.png"), (50, 100))  # Neutral
        self.car_sprite_left = load_image(os.path.join(assets_path, "car_left.png"), (50, 100))  # Izquierda
        self.car_sprite_right = load_image(os.path.join(assets_path, "car_right.png"), (50, 100))  # Derecha

        self.current_car_sprite = self.car_sprite  # Sprite actual del coche

        # Variable para rastrear el desplazamiento anterior
        self.previous_player_offset = 0.0

        # colores
        self.SKY_COLOR = (1, 10, 28)
        self.GRASS_COLOR = (0, 50, 0)
        self.ROAD_COLOR = (60, 60, 60)
        self.LINE_COLOR = (230, 230, 230)
        self.CURB_COLORS = [(255,0,0), (255,255,255)]

        # segmentos y perspectiva
        self.NUM_SEGMENTS = 60
        self.segment_height = max(4, (self.HEIGHT // 2) // self.NUM_SEGMENTS)

        # distancia / velocidad
        self.distance = 0.0
        self.base_road_speed = 2.0
        self.road_speed = self.base_road_speed

        # fases
        self.DASH_SPACING = 5
        self.CURB_SPACING = 3
        self.SIDE_LINE_SPACING = 3
        self.dash_phase = 0.0
        self.curb_phase = 0.0
        self.side_phase = 0.0
        self.DASH_PHASE_SPEED = 0.6
        self.CURB_PHASE_SPEED = 0.8
        self.SIDE_PHASE_SPEED = 0.7

        # city image (opcional)
        self.city_img = load_image(os.path.join(assets_path, "city.png"), (self.WIDTH, 140))

        # fog (ahora integrado)
        self.fog_height = 90
        self.fog_surf = make_fog_surf(self.WIDTH, self.fog_height, self.SKY_COLOR)

        # --- Track & Minimap ---
        self.track = Track(segment_height=self.segment_height, offset_scale=60.0, curve_strength=0.5)
        self.minimap = Minimap(self.screen, self.track)

    def update(self, dt):
         # --- Control de velocidad según la mano ---
        if self.state["value"] == "ABIERTA":
        # Acelera suavemente hasta un máximo
            self.road_speed = min(self.road_speed + 0.05, 10.0)
        else:
        # Desacelera suavemente hasta la velocidad base
            self.road_speed = max(self.road_speed - 0.08, 0.0)
        
        self.distance += self.road_speed * dt * 60.0
        self.dash_phase += self.road_speed * self.DASH_PHASE_SPEED * dt
        self.curb_phase += self.road_speed * self.CURB_PHASE_SPEED * dt
        self.side_phase += self.road_speed * self.SIDE_PHASE_SPEED * dt

        total_track_pixels = self.track.track_len * self.segment_height
        if self.distance >= total_track_pixels:
            self.distance -= total_track_pixels

    def get_closest_road_info(self):
        return self.track.get_closest_road_info(self.distance, self.WIDTH, self.NUM_SEGMENTS)

    def draw_minimap(self, sx, sy, sw, sh, player_distance=None, player_offset=0.0):
        # delega a Minimap (método disponible si necesitas llamarlo desde fuera)
        self.minimap.draw(sx, sy, sw, sh, player_distance=player_distance, player_offset=player_offset)

    def draw(self, player_offset=0.0, show_minimap=True):
        # Fondo cielo
        self.screen.fill(self.SKY_COLOR)

        # ciudad
        city_y = 170
        if self.city_img:
            self.screen.blit(self.city_img, (0, city_y))
            dark = pygame.Surface((self.WIDTH, self.city_img.get_height()), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 160))
            self.screen.blit(dark, (0, city_y))

        # pasto
        gfx.box(self.screen, (0, self.HEIGHT//2, self.WIDTH, self.HEIGHT//2), self.GRASS_COLOR)

        current_index = int(self.distance // self.segment_height) % self.track.track_len

        for i in range(self.NUM_SEGMENTS):
            perspective = (self.NUM_SEGMENTS - i) / self.NUM_SEGMENTS
            fade_t = 1.0 - perspective**1.8
            seg_road_color = blend_color(self.ROAD_COLOR, self.SKY_COLOR, fade_t * 0.95)

            road_w = int(self.WIDTH * 0.9 * perspective)
            idx = (current_index + i) % self.track.track_len

            # call track for center shift
            center_shift = self.track.center_shift(current_index, idx, perspective)

            player_px = int(player_offset * road_w * 0.35)
            center_x = self.WIDTH // 2 + center_shift - player_px

            x1 = center_x - road_w // 2
            x2 = center_x + road_w // 2
            y = int(self.HEIGHT - i * self.segment_height)

            # siguiente segmento
            next_i = i + 1
            next_perspective = (self.NUM_SEGMENTS - next_i) / self.NUM_SEGMENTS
            next_road_w = int(self.WIDTH * 0.9 * next_perspective)
            next_idx = (idx + 1) % self.track.track_len
            next_center_shift = self.track.center_shift(current_index, next_idx, next_perspective)
            next_player_px = int(player_offset * next_road_w * 0.35)
            next_center_x = self.WIDTH // 2 + next_center_shift - next_player_px

            next_x1 = next_center_x - next_road_w // 2
            next_x2 = next_center_x + next_road_w // 2
            next_y = y - self.segment_height

            side_offset = int(40 * perspective)
            next_side_offset = int(40 * next_perspective)

            bottom_left = (int(x1 - side_offset), int(y))
            bottom_right = (int(x2 + side_offset), int(y))
            top_right = (int(next_x2 + next_side_offset), int(next_y))
            top_left = (int(next_x1 - next_side_offset), int(next_y))

            pts = [bottom_left, bottom_right, top_right, top_left]
            gfx.filled_polygon(self.screen, pts, seg_road_color)
            gfx.aapolygon(self.screen, pts, seg_road_color)

            # líneas laterales
            if (i + int(self.side_phase)) % self.SIDE_LINE_SPACING == 0:
                lane_line_offset = int(road_w * 0.15)
                left_x = int(center_x - lane_line_offset)
                right_x = int(center_x + lane_line_offset)
                atten_line_color = blend_color(self.LINE_COLOR, self.SKY_COLOR, fade_t * 0.9)
                draw_aaline(self.screen, left_x, y+2, left_x, next_y-2, atten_line_color)
                draw_aaline(self.screen, right_x, y+2, right_x, next_y-2, atten_line_color)

            # dash central
            if (i + int(self.dash_phase)) % self.DASH_SPACING == 0:
                dash_w = max(8, int(road_w * 0.08))
                dash_h = max(6, int(self.segment_height * 0.9))
                dx1 = int(center_x - dash_w//2)
                dx2 = int(center_x + dash_w//2)
                nxw = max(2, int(dash_w * (next_perspective / (perspective + 1e-6))))
                ndx1 = int(next_center_x - nxw//2)
                ndx2 = int(next_center_x + nxw//2)
                dash_pts = [(dx1, int(y - self.segment_height*0.18)),
                            (dx2, int(y - self.segment_height*0.18)),
                            (ndx2, int(next_y + self.segment_height*0.12)),
                            (ndx1, int(next_y + self.segment_height*0.12))]
                dc = blend_color(self.LINE_COLOR, self.SKY_COLOR, fade_t*0.95)
                gfx.filled_polygon(self.screen, dash_pts, dc)
                gfx.aapolygon(self.screen, dash_pts, dc)

            # curbs
            if (i + int(self.curb_phase)) % self.CURB_SPACING == 0:
                curb_w = max(6, int(20 * perspective))
                curb_h = max(6, int(self.segment_height * 0.9))
                left_cx = int(x1 - side_offset - curb_w)
                right_cx = int(x2 + side_offset)
                color = self.CURB_COLORS[(i // self.CURB_SPACING) % 2]
                color_faded = blend_color(color, self.SKY_COLOR, min(0.95, fade_t * 1.1))
                gfx.box(self.screen, (left_cx, y, curb_w, curb_h), color_faded)
                gfx.box(self.screen, (right_cx, y, curb_w, curb_h), color_faded)

        # niebla (ahora integrada)
        self.screen.blit(self.fog_surf, (0, 140))

        # minimapa
        if show_minimap:
            mm_w = 200
            mm_h = 120
            mm_x = self.WIDTH - mm_w - 10
            mm_y = 8
            self.minimap.draw(mm_x, mm_y, mm_w, mm_h, player_distance=self.distance, player_offset=player_offset)
