from __future__ import annotations

from pathlib import Path

import pandas as pd

from simulacion_educativa.ai_personalized_scenario import AIPersonalizedScenario
from simulacion_educativa.config import SimulationConfig
from simulacion_educativa.ml.predictor import RiskPredictor
from simulacion_educativa.technology_scenario import TechnologyScenario
from simulacion_educativa.traditional_scenario import TraditionalScenario
from simulacion_educativa.visualization.final_dashboard import build_summary_frame, show_final_dashboard


def print_kpis(title: str, kpis: dict) -> None:
    print(f"\n=== {title} ===\n")

    for key, value in kpis.items():
        print(f"{key}: {value}")


def save_result_csv(result: dict, filename_prefix: str) -> None:
    output_path = Path("outputs/results")
    output_path.mkdir(parents=True, exist_ok=True)

    result["dataframe"].to_csv(
        output_path / f"{filename_prefix}_students.csv",
        index=False,
    )

    pd.DataFrame([result["kpis"]]).to_csv(
        output_path / f"{filename_prefix}_kpis.csv",
        index=False,
    )


def build_simulation_config() -> SimulationConfig:
    return SimulationConfig(
        num_students=100,
        semester_weeks=16,
        passing_grade=11.0,
        random_seed=42,
    )


def run_traditional(
    sim_config: SimulationConfig,
    cohort: list,
    *,
    animate: bool,
    speed: float,
) -> dict:
    scenario = TraditionalScenario(sim_config=sim_config, cohort=cohort)
    result = scenario.run_with_animation(animate=animate, speed=speed)
    result["key"] = "traditional"
    save_result_csv(result, "traditional_scenario")
    return result


def run_technology(
    sim_config: SimulationConfig,
    cohort: list,
    *,
    animate: bool,
    speed: float,
) -> dict:
    scenario = TechnologyScenario(sim_config=sim_config, cohort=cohort)
    result = scenario.run_with_animation(animate=animate, speed=speed)
    result["key"] = "technology"
    save_result_csv(result, "technology_scenario")
    return result


def run_ai(
    sim_config: SimulationConfig,
    cohort: list,
    *,
    animate: bool,
    speed: float,
) -> dict:
    predictor = RiskPredictor(model_path="outputs/models/best_risk_model.joblib")
    scenario = AIPersonalizedScenario(
        sim_config=sim_config,
        cohort=cohort,
        predictor=predictor,
    )
    result = scenario.run_with_animation(animate=animate, speed=speed)
    result["key"] = "ai"
    save_result_csv(result, "ai_personalized_scenario")
    return result


def run_scene(
    scene_key: str,
    sim_config: SimulationConfig,
    cohort: list,
    *,
    animate: bool,
    speed: float,
) -> dict:
    if scene_key == "traditional":
        return run_traditional(sim_config, cohort, animate=animate, speed=speed)

    if scene_key == "technology":
        return run_technology(sim_config, cohort, animate=animate, speed=speed)

    if scene_key == "ai":
        return run_ai(sim_config, cohort, animate=animate, speed=speed)

    raise ValueError(f"Escena desconocida: {scene_key}")


def run_scenes(
    scene_keys: list[str],
    sim_config: SimulationConfig,
    cohort_factory,
    base_cohort,
    *,
    animate: bool,
    speed: float,
    show_dashboard: bool = True,
) -> list[dict]:
    results = []

    for scene_key in scene_keys:
        cohort = cohort_factory.clone_cohort(base_cohort)
        result = run_scene(
            scene_key,
            sim_config,
            cohort,
            animate=animate,
            speed=speed,
        )
        results.append(result)
        print_kpis(result["scenario"], result["kpis"])

    comparison_df = build_summary_frame(results)

    output_path = Path("outputs/results")
    output_path.mkdir(parents=True, exist_ok=True)

    comparison_df.to_csv(
        output_path / "scenario_comparison.csv",
        index=False,
    )

    if len(results) > 1:
        print("\n=== COMPARACIÓN DE ESCENARIOS ===\n")
        print(comparison_df)

    if animate and show_dashboard:
        show_final_dashboard(results, scene_keys, speed=speed)

    return results
