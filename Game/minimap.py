import pygame
import pygame.gfxdraw as gfx
import math
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from track import Track

class Minimap:
    def __init__(self, screen, track):
        """
        track: instancia de Track (no se importa en tiempo de ejecución para evitar circular imports)
        """
        self.screen = screen
        self.track = track

    def draw(self, sx, sy, sw, sh, player_distance=None, player_offset=0.0):
        """
        Dibuja minimapa en rect (sx,sy,sw,sh).
        player_distance: distancia en px sobre la pista para ubicar el marcador.
        player_offset: -1..1 lateral (desplaza el marcador perpendicularmente).
        """
        pad = 4
        gfx.box(self.screen, (sx, sy, sw, sh), (10, 10, 10))
        inner = (sx + pad, sy + pad, sw - pad*2, sh - pad*2)

        pts = self.track.path_points
        if not pts:
            return

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        w = maxx - minx if maxx != minx else 1.0
        h = maxy - miny if maxy != miny else 1.0

        margin = 6
        scale_x = (inner[2] - margin*2) / w
        scale_y = (inner[3] - margin*2) / h
        scale = min(scale_x, scale_y)

        cx = inner[0] + inner[2]//2
        cy = inner[1] + inner[3]//2

        mini_pts = []
        for (x,y) in pts:
            mx = cx + int((x - (minx + maxx)/2) * scale)
            my = cy + int((y - (miny + maxy)/2) * scale)
            mini_pts.append((mx, my))

        if len(mini_pts) > 1:
            pygame.draw.lines(self.screen, (200,200,200), True, mini_pts, 2)
            pygame.draw.lines(self.screen, (40,40,40), True, mini_pts, max(6, int(6*scale)))

        start_pt = mini_pts[0]
        gfx.filled_circle(self.screen, start_pt[0], start_pt[1], 4, (0,255,0))
        gfx.circle(self.screen, start_pt[0], start_pt[1], 6, (0,255,0))

        if player_distance is not None:
            total_px = self.track.track_len * self.track.segment_height
            progress = (player_distance % total_px) / float(total_px)
            idx_f = progress * len(mini_pts)
            idx = int(idx_f) % len(mini_pts)
            next_idx = (idx + 1) % len(mini_pts)
            frac = idx_f - idx
            x1,y1 = mini_pts[idx]
            x2,y2 = mini_pts[next_idx]
            px = int(x1 + (x2-x1)*frac)
            py = int(y1 + (y2-y1)*frac)

            tx = x2 - x1
            ty = y2 - y1
            leng = math.hypot(tx, ty) or 1.0
            nx = -ty / leng
            ny = tx / leng
            track_width_px = max(6, int(6 * scale))
            lateral_shift = int(player_offset * 0.5 * track_width_px)
            px2 = px + int(nx * lateral_shift)
            py2 = py + int(ny * lateral_shift)

            size = 6
            ux = tx / (leng or 1.0)
            uy = ty / (leng or 1.0)
            pA = (px2 + int(ux * size), py2 + int(uy * size))
            pB = (px2 + int(-uy * (size//2)), py2 + int( ux * (size//2)))
            pC = (px2 + int( uy * (size//2)), py2 + int(-ux * (size//2)))
            gfx.filled_polygon(self.screen, [pA,pB,pC], (255, 220, 20))
            gfx.aapolygon(self.screen, [pA,pB,pC], (255,200,20))

        gfx.aapolygon(self.screen, [(inner[0],inner[1]),(inner[0]+inner[2],inner[1]),(inner[0]+inner[2],inner[1]+inner[3]),(inner[0],inner[1]+inner[3])], (80,80,80))
