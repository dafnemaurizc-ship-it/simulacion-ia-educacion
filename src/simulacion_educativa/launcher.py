from __future__ import annotations

from dataclasses import dataclass

from simulacion_educativa.cohort_factory import CohortFactory
from simulacion_educativa.runner import build_simulation_config, run_scenes


SCENE_MENU = {
    "1": (("traditional",), "Educación tradicional"),
    "2": (("technology",), "Uso de tecnología educativa"),
    "3": (("ai",), "Educación personalizada con IA"),
    "4": (("traditional", "technology", "ai"), "Comparar las 3 escenas"),
}


@dataclass(slots=True)
class LauncherChoice:
    scene_keys: list[str]
    label: str
    animate: bool
    speed: float


def _read_bool(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"{prompt} {suffix}: ").strip().lower()
    if not raw:
        return default
    return raw in {"y", "yes", "s", "si", "sí", "1"}


def _read_float(prompt: str, default: float = 1.0) -> float:
    raw = input(f"{prompt} [{default}]: ").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        print("Valor inválido, usando el valor por defecto.")
        return default


def _print_menu() -> None:
    print("\n=== Launcher interactivo ===\n")
    for key, (_, label) in SCENE_MENU.items():
        print(f"{key}. {label}")
    print("0. Salir")


def _read_choice() -> str:
    return input("Elegí una opción: ").strip()


def _resolve_choice(choice: str) -> LauncherChoice | None:
    if choice not in SCENE_MENU:
        return None

    scene_keys, label = SCENE_MENU[choice]
    animate = _read_bool("¿Ejecutar con animación en tiempo real?", default=True)
    speed = _read_float("Velocidad de animación", default=1.0)

    return LauncherChoice(
        scene_keys=list(scene_keys),
        label=label,
        animate=animate,
        speed=speed,
    )


def run_interactive_launcher() -> None:
    sim_config = build_simulation_config()
    cohort_factory = CohortFactory(sim_config)
    base_cohort = cohort_factory.create_cohort()

    while True:
        _print_menu()
        choice = _read_choice()

        if choice == "0":
            print("Saliendo del launcher.")
            return

        resolved = _resolve_choice(choice)
        if resolved is None:
            print("Opción inválida.")
            continue

        print(f"\nEjecutando: {resolved.label}\n")
        run_scenes(
            resolved.scene_keys,
            sim_config,
            cohort_factory,
            base_cohort,
            animate=resolved.animate,
            speed=resolved.speed,
            show_dashboard=True,
        )
