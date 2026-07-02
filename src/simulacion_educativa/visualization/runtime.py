from __future__ import annotations

import salabim as sim

from simulacion_educativa.visualization.styles import WINDOW_HEIGHT, WINDOW_WIDTH


def build_environment(
    *,
    animate: bool,
    title: str,
    speed: float = 1.0,
    width: int = WINDOW_WIDTH,
    height: int = WINDOW_HEIGHT,
) -> sim.Environment:
    if animate and sim.can_animate():
        env = sim.Environment(
            width=width,
            height=height,
            speed=speed,
            show_fps=True,
            blind_animation=False,
        )
        env.animation_parameters(
            title=title,
            show_menu_buttons=False,
            speed=speed,
            x0=0,
            y0=0,
            x1=width,
            animate=True,
        )
        return env

    if animate and not sim.can_animate():
        print("Animacion no disponible en este entorno; se ejecuta en modo batch.")

    return sim.Environment(trace=False)
