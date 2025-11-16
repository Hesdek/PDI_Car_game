import pygame
import pygame.gfxdraw as gfx
import os

def lerp(a, b, t):
    return a + (b - a) * t

def blend_color(c1, c2, t):
    return (int(lerp(c1[0], c2[0], t)),
            int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)))

def _to_int_color(col):
    return (int(col[0]), int(col[1]), int(col[2]))

def draw_aaline(surface, x1, y1, x2, y2, color):
    """Dibuja una línea anti-aliased con fallback seguro."""
    x1_i, y1_i, x2_i, y2_i = int(x1), int(y1), int(x2), int(y2)
    color_i = _to_int_color(color)
    try:
        gfx.aaline(surface, x1_i, y1_i, x2_i, y2_i, color_i)
        return
    except Exception:
        pass
    try:
        pygame.draw.aaline(surface, color_i, (x1_i, y1_i), (x2_i, y2_i))
        return
    except Exception:
        pass
    pygame.draw.line(surface, color_i, (x1_i, y1_i), (x2_i, y2_i))

def load_image(path, size=None, colorkey=None):
    """Carga imagen y la escala si size dado. Devuelve surface o None."""
    if not os.path.isfile(path):
        return None
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    if colorkey is not None:
        img.set_colorkey(colorkey)
    return img
