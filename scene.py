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

        # --- colores ---
        self.SKY_COLOR = (1, 10, 28)
        self.GRASS_COLOR = (0, 50, 0)
        self.ROAD_COLOR = (60, 60, 60)
        self.LINE_COLOR = (230, 230, 230)
        self.CURB_COLORS = [(255,0,0), (255,255,255)]

        # segmentos y perspectiva (más segmentos -> curvas más suaves)
        self.NUM_SEGMENTS = 60
        self.segment_height = max(4, (self.HEIGHT // 2) // self.NUM_SEGMENTS)

        # avance a lo largo de la pista (reducido para que no pase tan rápido)
        self.distance = 0.0
        self.road_speed = 3.0  # disminuir => la pista "pasa" más despacio

        # fases animadas
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

        # niebla
        self.fog_height = 90
        small_w = 200
        small_fog = pygame.Surface((small_w, self.fog_height), pygame.SRCALPHA)
        for r in range(self.fog_height):
            t = r / max(1, self.fog_height - 1)
            alpha = int(180 * (t ** 1.4))
            gfx.box(small_fog, (0, r, small_w, 1), (self.SKY_COLOR[0], self.SKY_COLOR[1], self.SKY_COLOR[2], alpha))
        self.fog_surf = pygame.transform.smoothscale(small_fog, (self.WIDTH, self.fog_height)).convert_alpha()

        # --- pista (circuito) ---
        self.track = self.build_circuit()
        self.track_len = len(self.track)

        # escala en px para convertir curvatura a desplazamiento horizontal
        self.offset_scale = 60.0   # reducido para curvas menos pronunciadas
        self.curve_strength = 0.5  # multiplicador adicional para "apaciguar" curvas

    def build_circuit(self):
        # Circuito simple: rectas y curvas pequeñas
        track = []
        pattern = [
            (30, 0.0),    # recta
            (50, 0.35),   # curva derecha (más suave)
            (30, 0.0),
            (50, -0.35),  # curva izquierda (más suave)
            (40, 0.0)
        ]
        for length, curve in pattern:
            for _ in range(length):
                track.append(curve)
        return track

    def update(self, dt):
        # avanzar distancia y fases (usa dt en segundos)
        # multiplico por 60 para mantener "sensación" similar si venías de tick-based
        self.distance += self.road_speed * dt * 60.0
        self.dash_phase += self.road_speed * self.DASH_PHASE_SPEED * dt
        self.curb_phase += self.road_speed * self.CURB_PHASE_SPEED * dt
        self.side_phase += self.road_speed * self.SIDE_PHASE_SPEED * dt

        # wrap para circuito
        total_track_pixels = self.track_len * self.segment_height
        if self.distance >= total_track_pixels:
            self.distance -= total_track_pixels

    def _accumulated_curve(self, start_idx, end_idx):
        # suma simple de curvaturas desde start_idx hasta end_idx (inclusive).
        # Puedes cambiar esto por un suavizado más complejo si deseas.
        s = 0.0
        j = start_idx
        while True:
            s += self.track[j % self.track_len]
            if j % self.track_len == end_idx:
                break
            j += 1
        return s

    def draw(self, player_offset=0.0):
        # fondo cielo
        self.screen.fill(self.SKY_COLOR)

        # ciudad
        city_y = 170
        if self.city_img:
            self.screen.blit(self.city_img, (0, city_y))
            dark = pygame.Surface((self.WIDTH, self.city_img.get_height()), pygame.SRCALPHA)
            dark.fill((0,0,0,160))
            self.screen.blit(dark, (0, city_y))

        # pasto
        gfx.box(self.screen, (0, self.HEIGHT//2, self.WIDTH, self.HEIGHT//2), self.GRASS_COLOR)

        current_index = int(self.distance // self.segment_height) % self.track_len

        for i in range(self.NUM_SEGMENTS):
            perspective = (self.NUM_SEGMENTS - i) / self.NUM_SEGMENTS
            fade_t = 1.0 - perspective**1.8
            seg_road_color = blend_color(self.ROAD_COLOR, self.SKY_COLOR, fade_t * 0.95)

            road_w = int(self.WIDTH * 0.9 * perspective)

            idx = (current_index + i) % self.track_len

            # acumulado de curvatura (más suave porque las curvaturas en track ya son pequeñas)
            curve_sum = self._accumulated_curve(current_index, idx)

            # aplicar fuerza y escala reducida para que las curvas no sean enormes
            center_shift = int(curve_sum * self.offset_scale * self.curve_strength * (perspective**0.9))

            # offset del jugador (coche estacionario en el centro)
            player_px = int(player_offset * road_w * 0.35)
            center_x = self.WIDTH // 2 + center_shift - player_px

            x1 = center_x - road_w // 2
            x2 = center_x + road_w // 2
            y = int(self.HEIGHT - i * self.segment_height)

            # siguiente segmento (aprox)
            next_i = i + 1
            next_perspective = (self.NUM_SEGMENTS - next_i) / self.NUM_SEGMENTS
            next_road_w = int(self.WIDTH * 0.9 * next_perspective)
            next_idx = (idx + 1) % self.track_len
            next_curve_sum = curve_sum + self.track[next_idx]
            next_center_shift = int(next_curve_sum * self.offset_scale * self.curve_strength * (next_perspective**0.9))
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

        # niebla
        def get_closest_road_info(self):
            current_index = int(self.distance // self.segment_height) % self.track_len
            i = 0  # segmento más cercano que dibujamos en draw()
            perspective = (self.NUM_SEGMENTS - i) / self.NUM_SEGMENTS
            road_w = int(self.WIDTH * 0.9 * perspective)

            # calculamos curve_sum desde current_index hasta idx=current_index (solo primer segmento)
            # aquí la suma es solo self.track[current_index] pero la dejamos general por claridad
            curve_sum = 0.0
            j = current_index
            while True:
                curve_sum += self.track[j % self.track_len]
                if j % self.track_len == current_index:
                    break
                j += 1

            center_shift = int(curve_sum * self.offset_scale * self.curve_strength * (perspective**0.9))
            center_x = self.WIDTH // 2 + center_shift

            return center_x, road_w, current_index, curve_sum

        self.screen.blit(self.fog_surf, (0, 140))
