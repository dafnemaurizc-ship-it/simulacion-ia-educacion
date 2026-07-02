from pathlib import Path

import pandas as pd

from simulacion_educativa.ai_personalized_scenario import AIPersonalizedScenario
from simulacion_educativa.cohort_factory import CohortFactory
from simulacion_educativa.config import SimulationConfig
from simulacion_educativa.ml.predictor import RiskPredictor
from simulacion_educativa.technology_scenario import TechnologyScenario
from simulacion_educativa.traditional_scenario import TraditionalScenario


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


def main() -> None:
    sim_config = SimulationConfig(
        num_students=100,
        semester_weeks=16,
        passing_grade=11.0,
        random_seed=42,
    )

    cohort_factory = CohortFactory(sim_config)
    base_cohort = cohort_factory.create_cohort()

    traditional_cohort = cohort_factory.clone_cohort(base_cohort)
    technology_cohort = cohort_factory.clone_cohort(base_cohort)
    ai_cohort = cohort_factory.clone_cohort(base_cohort)

    predictor = RiskPredictor(
        model_path="outputs/models/best_risk_model.joblib",
    )

    traditional = TraditionalScenario(
        sim_config=sim_config,
        cohort=traditional_cohort,
    )

    technology = TechnologyScenario(
        sim_config=sim_config,
        cohort=technology_cohort,
    )

    ai_personalized = AIPersonalizedScenario(
        sim_config=sim_config,
        cohort=ai_cohort,
        predictor=predictor,
    )

    traditional_result = traditional.run()
    technology_result = technology.run()
    ai_result = ai_personalized.run()

    save_result_csv(traditional_result, "traditional_scenario")
    save_result_csv(technology_result, "technology_scenario")
    save_result_csv(ai_result, "ai_personalized_scenario")

    print_kpis(
        "ESCENARIO 1: EDUCACIÓN TRADICIONAL",
        traditional_result["kpis"],
    )

    print_kpis(
        "ESCENARIO 2: USO DE TECNOLOGÍA EDUCATIVA",
        technology_result["kpis"],
    )

    print_kpis(
        "ESCENARIO 3: EDUCACIÓN PERSONALIZADA CON IA",
        ai_result["kpis"],
    )

    comparison_df = pd.DataFrame(
        [
            {
                "scenario": traditional_result["scenario"],
                **traditional_result["kpis"],
            },
            {
                "scenario": technology_result["scenario"],
                **technology_result["kpis"],
            },
            {
                "scenario": ai_result["scenario"],
                **ai_result["kpis"],
            },
        ]
    )

    output_path = Path("outputs/results")
    output_path.mkdir(parents=True, exist_ok=True)

    comparison_df.to_csv(
        output_path / "scenario_comparison.csv",
        index=False,
    )

    print("\n=== COMPARACIÓN DE ESCENARIOS ===\n")
    print(comparison_df)


if __name__ == "__main__":
    main()
