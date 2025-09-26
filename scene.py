import pygame
import pygame.gfxdraw as gfx
import os
from utils import blend_color, draw_aaline, load_image

class Scene:
    def __init__(self, screen, width, height, assets_path="assets"):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height
        self.assets_path = assets_path

        # Colores y parámetros (puedes ajustar)
        self.SKY_COLOR = (6, 10, 40)
        self.GRASS_COLOR = (0, 50, 0)
        self.ROAD_COLOR = (60, 60, 60)
        self.LINE_COLOR = (230, 230, 230)
        self.CURB_COLORS = [(255,0,0), (255,255,255)]

        # segmentos y perspectiva
        self.NUM_SEGMENTS = 28
        self.segment_height = max(6, (self.HEIGHT // 2) // self.NUM_SEGMENTS)

        # velocidad y scroll
        self.scroll = 0.0
        self.road_speed = 6.5

        # spacing y fases para ilusión de movimiento
        self.DASH_SPACING = 5
        self.CURB_SPACING = 3
        self.SIDE_LINE_SPACING = 3

        self.dash_phase = 0.0
        self.curb_phase = 0.0
        self.side_phase = 0.0
        self.DASH_PHASE_SPEED = 1.0
        self.CURB_PHASE_SPEED = 1.05
        self.SIDE_PHASE_SPEED = 0.9

        # Cargar ciudad
        try:
            self.city_img = load_image(os.path.join(assets_path, "city.png"), (self.WIDTH, 140))
        except Exception:
            self.city_img = None

        # precalcular niebla (a baja resol y smoothscale para evitar banding)
        self.fog_height = 90
        small_w = 200
        small_fog = pygame.Surface((small_w, self.fog_height), pygame.SRCALPHA)
        for r in range(self.fog_height):
            t = r / max(1, self.fog_height - 1)
            alpha = int(180 * (t ** 1.4))
            gfx.box(small_fog, (0, r, small_w, 1), (self.SKY_COLOR[0], self.SKY_COLOR[1], self.SKY_COLOR[2], alpha))
        self.fog_surf = pygame.transform.smoothscale(small_fog, (self.WIDTH, self.fog_height)).convert_alpha()

    def update(self, dt):
        # actualizar scroll y fases
        self.scroll += self.road_speed * dt * 60.0
        if self.scroll >= self.segment_height:
            self.scroll -= self.segment_height
        self.dash_phase += self.road_speed * self.DASH_PHASE_SPEED * dt
        self.curb_phase += self.road_speed * self.CURB_PHASE_SPEED * dt
        self.side_phase += self.road_speed * self.SIDE_PHASE_SPEED * dt

    def draw(self, player_x=None):
        # cielo
        self.screen.fill(self.SKY_COLOR)

        # ciudad
        city_y = 170
        if self.city_img:
            self.screen.blit(self.city_img, (0, city_y))
            dark = pygame.Surface((self.WIDTH, self.city_img.get_height()), pygame.SRCALPHA)
            dark.fill((0,0,0,160))
            self.screen.blit(dark, (0, city_y))
        else:
            # fallback edificios simples
            for i in range(20):
                bw = 30 + (i % 4) * 10
                bh = 40 + (i % 6) * 20
                bx = i * (self.WIDTH // 20)
                by = city_y + 100 - bh
                gfx.box(self.screen, (bx, by, bw, bh), (30,30,60))

        # pasto
        gfx.box(self.screen, (0, self.HEIGHT//2, self.WIDTH, self.HEIGHT//2), self.GRASS_COLOR)

        # dibujar road por segmentos
        for i in range(self.NUM_SEGMENTS):
            perspective = (self.NUM_SEGMENTS - i) / self.NUM_SEGMENTS
            fade_t = 1.0 - perspective**1.8
            seg_road_color = blend_color(self.ROAD_COLOR, self.SKY_COLOR, fade_t * 0.95)

            road_w = int(self.WIDTH * 0.9 * perspective)
            x1 = self.WIDTH // 2 - road_w // 2
            x2 = self.WIDTH // 2 + road_w // 2
            y = int(self.HEIGHT - i * self.segment_height + self.scroll)

            if self.HEIGHT // 2 - self.segment_height < y < self.HEIGHT + self.segment_height:
                next_i = min(i + 1, self.NUM_SEGMENTS - 1)
                next_perspective = (self.NUM_SEGMENTS - next_i) / self.NUM_SEGMENTS
                next_road_w = int(self.WIDTH * 0.9 * next_perspective)
                next_x1 = self.WIDTH // 2 - next_road_w // 2
                next_x2 = self.WIDTH // 2 + next_road_w // 2
                next_y = y + self.segment_height

                side_offset = int(40 * perspective)
                next_side_offset = int(40 * next_perspective)

                bottom_left = (int(x1 - side_offset), int(y))
                bottom_right = (int(x2 + side_offset), int(y))
                top_right = (int(next_x2 + next_side_offset), int(next_y))
                top_left = (int(next_x1 - next_side_offset), int(next_y))

                pts = [bottom_left, bottom_right, top_right, top_left]
                gfx.filled_polygon(self.screen, pts, seg_road_color)
                gfx.aapolygon(self.screen, pts, seg_road_color)

                # lineas laterales (menos frecuentes)
                if (i + int(self.side_phase)) % self.SIDE_LINE_SPACING == 0:
                    lane_line_offset = int(road_w * 0.15)
                    left_x = int(self.WIDTH // 2 - lane_line_offset)
                    right_x = int(self.WIDTH // 2 + lane_line_offset)
                    atten_line_color = blend_color(self.LINE_COLOR, self.SKY_COLOR, fade_t * 0.9)
                    # aaline con fallback
                    draw_aaline(self.screen, left_x, y+2, left_x, next_y-2, atten_line_color)
                    draw_aaline(self.screen, right_x, y+2, right_x, next_y-2, atten_line_color)

                # dash central (animado por dash_phase)
                if (i + int(self.dash_phase)) % self.DASH_SPACING == 0:
                    dash_w = max(12, int(road_w * 0.10))
                    dash_h = max(8, int(self.segment_height * 0.9))
                    dx1 = int(self.WIDTH//2 - dash_w//2)
                    dx2 = int(self.WIDTH//2 + dash_w//2)
                    nxw = max(2, int(dash_w * (next_perspective / (perspective+1e-6))))
                    ndx1 = int(self.WIDTH//2 - nxw//2)
                    ndx2 = int(self.WIDTH//2 + nxw//2)
                    dash_pts = [(dx1, int(y + self.segment_height*0.18)),
                                (dx2, int(y + self.segment_height*0.18)),
                                (ndx2, int(next_y - self.segment_height*0.12)),
                                (ndx1, int(next_y - self.segment_height*0.12))]
                    dc = blend_color(self.LINE_COLOR, self.SKY_COLOR, fade_t*0.95)
                    gfx.filled_polygon(self.screen, dash_pts, dc)
                    gfx.aapolygon(self.screen, dash_pts, dc)

                # curbs
                if (i + int(self.curb_phase)) % self.CURB_SPACING == 0:
                    curb_w = max(8, int(28 * perspective))
                    curb_h = max(8, int(self.segment_height * 0.9))
                    left_cx = int(x1 - side_offset - curb_w)
                    right_cx = int(x2 + side_offset)
                    color = self.CURB_COLORS[(i // self.CURB_SPACING) % 2]
                    color_faded = blend_color(color, self.SKY_COLOR, min(0.95, fade_t * 1.1))
                    gfx.box(self.screen, (left_cx, y, curb_w, curb_h), color_faded)
                    gfx.box(self.screen, (right_cx, y, curb_w, curb_h), color_faded)

        # niebla
        self.screen.blit(self.fog_surf, (0, 140))
