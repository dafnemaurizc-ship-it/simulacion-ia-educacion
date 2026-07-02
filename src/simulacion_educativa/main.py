from __future__ import annotations

from argparse import ArgumentParser, Namespace

from simulacion_educativa.cohort_factory import CohortFactory
from simulacion_educativa.launcher import run_interactive_launcher
from simulacion_educativa.runner import build_simulation_config, run_scenes

SCENE_KEYS = ("traditional", "technology", "ai")


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Simulación educativa con IA")
    parser.add_argument(
        "--animate",
        action="store_true",
        help="Habilita la animación en tiempo real con Salabim.",
    )
    parser.add_argument(
        "--scenario",
        choices=["all", *SCENE_KEYS],
        default="all",
        help="Escenario único a ejecutar.",
    )
    parser.add_argument(
        "--scenes",
        nargs="+",
        choices=SCENE_KEYS,
        help="Escenas a ejecutar en orden.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Velocidad de reproducción de la animación.",
    )
    parser.add_argument(
        "--launcher",
        action="store_true",
        help="Abre el launcher interactivo por terminal.",
    )

    return parser.parse_args()


def resolve_selected_scenes(args: Namespace) -> list[str]:
    if args.scenes:
        return list(args.scenes)

    if args.scenario != "all":
        return [args.scenario]

    return list(SCENE_KEYS)


def main() -> None:
    args = parse_args()

    if args.launcher:
        run_interactive_launcher()
        return

    selected_scenes = resolve_selected_scenes(args)

    sim_config = build_simulation_config()
    cohort_factory = CohortFactory(sim_config)
    base_cohort = cohort_factory.create_cohort()

    run_scenes(
        selected_scenes,
        sim_config,
        cohort_factory,
        base_cohort,
        animate=args.animate,
        speed=args.speed,
        show_dashboard=True,
    )


if __name__ == "__main__":
    main()
