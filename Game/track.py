# track.py
import math

class Track:
    def __init__(self, track_list=None, segment_height=6, offset_scale=60.0, curve_strength=0.5):
        """
        track_list: lista opcional de curvaturas por segmento. Si es None, usa build_circuit().
        segment_height: altura en px de cada segmento (para mapping distancia -> index).
        offset_scale, curve_strength: parámetros para convertir curvatura a desplazamiento en px.
        """
        self.segment_height = segment_height
        self.offset_scale = offset_scale
        self.curve_strength = curve_strength

        self.track = track_list if track_list is not None else self.build_circuit()
        self.track_len = len(self.track)

        # geometry para minimapa / debugging
        self.path_points, self.total_length = self._build_path_geometry(step_len=self.segment_height)

    def build_circuit(self):
        # Patrón base: ajusta aquí para cambiar la pista (determinística)
        track = []
        pattern = [
            (60, 0.0),
            (40, 0.6),
            (40, 0.0),
            (40, -0.4),
            (40, 0.0),
            (20, 0.30),
            (60, 0.5),
            (60, 0.0),
            (40, -0.5),
            (60, 0.0),
        ]
        for length, curve in pattern:
            for _ in range(length):
                track.append(curve)
        return track

    def _build_path_geometry(self, step_len=4):
        pts = []
        x = 0.0
        y = 0.0
        theta = 0.0
        scale = 1.0
        for c in self.track:
            theta += c * 0.2
            dx = math.sin(theta) * (step_len * scale)
            dy = -math.cos(theta) * (step_len * scale)
            x += dx
            y += dy
            pts.append((x, y))

        # --- CERRAR EL LAZO: interpolar entre último y primero si hay una brecha grande ---
        if len(pts) > 2:
            first = pts[0]
            last = pts[-1]
            gap = math.hypot(first[0] - last[0], first[1] - last[1])
            # umbral: si la brecha > 10% del tamaño total, rellenamos
            if gap > (step_len * 2):
                n_bridge = max(6, int(gap / (step_len * 0.8)))  # número de puntos puente
                for k in range(1, n_bridge):
                    t = k / float(n_bridge)
                    bx = last[0] + (first[0] - last[0]) * t
                    by = last[1] + (first[1] - last[1]) * t
                    pts.append((bx, by))

        total_length = len(pts) * step_len * scale
        # centrar
        if pts:
            sx = sum(p[0] for p in pts) / len(pts)
            sy = sum(p[1] for p in pts) / len(pts)
            pts = [(p[0] - sx, p[1] - sy) for p in pts]
        return pts, total_length


    def accumulated_curve(self, start_idx, end_idx):
        """Suma simple de curvaturas desde start_idx hasta end_idx (inclusive)."""
        s = 0.0
        j = start_idx
        while True:
            s += self.track[j % self.track_len]
            if j % self.track_len == end_idx:
                break
            j += 1
        return s

    def center_shift(self, current_index, idx, perspective):
        """Devuelve desplazamiento en px del centro de la carretera para el segmento idx
           cuando el índice actual (el más cercano) es current_index."""
        curve_sum = self.accumulated_curve(current_index, idx)
        return int(curve_sum * self.offset_scale * self.curve_strength * (perspective**0.9))

    def get_closest_road_info(self, distance, screen_width, num_segments):
        """
        Dado distance (en px acumulados), devuelve (center_x, road_w, current_index, curve_val)
        donde curve_val es la curvatura del segmento actual (no la suma).
        """
        current_index = int(distance // self.segment_height) % self.track_len
        i = 0
        perspective = (num_segments - i) / num_segments
        road_w = int(screen_width * 0.9 * perspective)

        # curva del segmento actual (o suma reducida si prefieres)
        curve_val = self.track[current_index % self.track_len]

        center_shift = self.center_shift(current_index, current_index, perspective)
        center_x = screen_width // 2 + center_shift
        return center_x, road_w, current_index, curve_val
