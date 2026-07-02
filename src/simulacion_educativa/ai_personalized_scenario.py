from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd
import salabim as sim

from simulacion_educativa.config import (
    AIPersonalizedScenarioConfig,
    SimulationConfig,
)
from simulacion_educativa.entities import StudentState
from simulacion_educativa.metrics import calculate_kpis, students_to_dataframe
from simulacion_educativa.ml.predictor import RiskPredictor
from simulacion_educativa.visualization import SalabimLiveView, build_environment

sim.yieldless(False)


class AIPersonalizedStudent(sim.Component):
    """
    Agente estudiante para el escenario 3: educación personalizada con IA.

    Cada estudiante es evaluado por el modelo ML y recibe una intervención
    personalizada según su nivel de riesgo académico.
    """

    def setup(
        self,
        state: StudentState,
        sim_config: SimulationConfig,
        scenario_config: AIPersonalizedScenarioConfig,
        predictor: RiskPredictor,
    ) -> None:
        self.state = state
        self.sim_config = sim_config
        self.scenario_config = scenario_config
        self.predictor = predictor

    def process(self):
        for _week in range(1, self.sim_config.semester_weeks + 1):
            if self.state.deserted:
                break

            self._predict_academic_risk()
            self._simulate_learning_week()
            self._update_desertion_risk()
            self._check_desertion()

            self.state.weeks_completed += 1

            yield self.hold(1)

        self._finalize_student()

    def _predict_academic_risk(self) -> None:
        """
        Usa el modelo ML para estimar riesgo académico.
        """

        student_features = self.state.to_ml_features()

        probability = self.predictor.predict_risk_probability(student_features)
        risk_level = self.predictor.classify_risk_level(student_features)

        self.state.ml_risk_probability = round(probability, 4)
        self.state.ml_risk_level = risk_level

    def _simulate_learning_week(self) -> None:
        """
        Calcula el avance semanal considerando personalización con IA.
        """

        cfg = self.scenario_config

        study_effect = (
            self.state.normalized_study_hours
            * cfg.study_weight
            * cfg.methodology_factor
            * 20
        )

        attendance_effect = (
            self.state.normalized_attendance
            * cfg.attendance_weight
            * cfg.methodology_factor
            * 20
        )

        motivation_effect = (
            self.state.normalized_motivation
            * cfg.motivation_weight
            * cfg.feedback_factor
            * 20
        )

        technology_effect = (
            self.state.technology_score
            * cfg.technology_weight
            * cfg.technology_factor
            * 20
        )

        personalization_effect = (
            self._get_ai_intervention_effect()
            * cfg.personalization_weight
            * cfg.personalization_factor
            * 20
        )

        penalty = self._calculate_penalty()
        noise = np.random.normal(cfg.noise_mean, cfg.noise_std)

        weekly_delta = (
            study_effect
            + attendance_effect
            + motivation_effect
            + technology_effect
            + personalization_effect
            - penalty
            + noise
        )

        self.state.current_grade += weekly_delta / self.sim_config.semester_weeks

        self.state.current_grade = min(
            max(self.state.current_grade, self.sim_config.min_grade),
            self.sim_config.max_grade,
        )

    def _get_ai_intervention_effect(self) -> float:
        """
        Define cuánto ayuda la IA según el riesgo detectado.

        La intervención también depende del acceso tecnológico.
        """

        cfg = self.scenario_config

        if self.state.ml_risk_level == "alto":
            base_effect = cfg.high_risk_intervention
        elif self.state.ml_risk_level == "medio":
            base_effect = cfg.medium_risk_intervention
        else:
            base_effect = cfg.low_risk_intervention

        # Si el acceso tecnológico es bajo, la IA ayuda menos.
        if self.state.technology_access == "bajo":
            return base_effect * 0.60

        if self.state.technology_access == "medio":
            return base_effect * 0.85

        return base_effect

    def _calculate_penalty(self) -> float:
        cfg = self.scenario_config
        penalty = 0.0

        if self.state.study_hours < 4:
            penalty += cfg.low_study_penalty

        if self.state.attendance < 70:
            penalty += cfg.low_attendance_penalty

        if self.state.motivation < 0.40:
            penalty += cfg.low_motivation_penalty

        if self.state.technology_access == "bajo":
            penalty += cfg.low_technology_penalty

        return penalty

    def _update_desertion_risk(self) -> None:
        """
        Actualiza riesgo de deserción considerando intervención IA.
        """

        cfg = self.scenario_config
        risk_growth = 0.0

        if self.state.current_grade < cfg.low_performance_threshold:
            risk_growth += cfg.weekly_risk_growth

        if self.state.study_hours < 4:
            risk_growth += 0.025

        if self.state.attendance < 70:
            risk_growth += 0.025

        if self.state.motivation < 0.40:
            risk_growth += 0.030

        if self.state.technology_access == "bajo":
            risk_growth += 0.030

        if risk_growth == 0.0:
            self.state.desertion_risk -= cfg.weekly_risk_reduction
        else:
            self.state.desertion_risk += risk_growth

        # Reducción por intervención IA.
        if self.state.ml_risk_level == "alto":
            self.state.desertion_risk -= 0.055
        elif self.state.ml_risk_level == "medio":
            self.state.desertion_risk -= 0.040
        else:
            self.state.desertion_risk -= 0.020

        # El bajo acceso limita la efectividad de la IA.
        if self.state.technology_access == "bajo":
            self.state.desertion_risk += 0.020

        self.state.desertion_risk = min(max(self.state.desertion_risk, 0.0), 1.0)

    def _check_desertion(self) -> None:
        cfg = self.scenario_config

        if self.state.desertion_risk >= cfg.desertion_risk_threshold:
            self.state.deserted = True

    def _finalize_student(self) -> None:
        self.state.final_grade = round(self.state.current_grade, 2)

        if self.state.deserted:
            self.state.approved = False
            return

        self.state.approved = self.state.final_grade >= self.sim_config.passing_grade


class AIPersonalizedScenario:
    """
    Escenario 3: educación personalizada con IA.
    """

    def __init__(
        self,
        sim_config: SimulationConfig | None = None,
        scenario_config: AIPersonalizedScenarioConfig | None = None,
        cohort: list[StudentState] | None = None,
        predictor: RiskPredictor | None = None,
    ) -> None:
        self.sim_config = sim_config or SimulationConfig()
        self.scenario_config = scenario_config or AIPersonalizedScenarioConfig()
        self.students: list[StudentState] = cohort or []
        self.predictor = predictor or RiskPredictor()

    def run(self) -> dict:
        return self.run_with_animation(animate=False)

    def run_with_animation(self, *, animate: bool, speed: float = 1.0) -> dict:
        random.seed(self.sim_config.random_seed)
        np.random.seed(self.sim_config.random_seed)

        env = build_environment(
            animate=animate,
            title="Educación personalizada con IA",
            speed=speed,
        )

        if not self.students:
            raise ValueError(
                "No se recibió una cohorte. Usa CohortFactory para generar estudiantes."
            )

        if animate:
            SalabimLiveView(
                env=env,
                students=self.students,
                scenario_name="Educación personalizada con IA",
                semester_weeks=self.sim_config.semester_weeks,
                show_ml_metrics=True,
            )

        for student_state in self.students:
            AIPersonalizedStudent(
                state=student_state,
                sim_config=self.sim_config,
                scenario_config=self.scenario_config,
                predictor=self.predictor,
                env=env,
            )

        env.run(till=self.sim_config.semester_weeks + 1)

        df = students_to_dataframe(self.students)
        kpis = calculate_kpis(df)

        return {
            "scenario": "Educación personalizada con IA",
            "dataframe": df,
            "kpis": kpis,
        }

    def save_results(self, output_dir: str = "outputs/results") -> None:
        result = self.run()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        result["dataframe"].to_csv(
            output_path / "ai_personalized_scenario_students.csv",
            index=False,
        )

        pd.DataFrame([result["kpis"]]).to_csv(
            output_path / "ai_personalized_scenario_kpis.csv",
            index=False,
        )
