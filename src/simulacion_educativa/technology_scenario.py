from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd
import salabim as sim

sim.yieldless(False)

from simulacion_educativa.config import (
    SimulationConfig,
    TechnologyScenarioConfig,
)
from simulacion_educativa.entities import AccessLevel, StudentState
from simulacion_educativa.metrics import calculate_kpis, students_to_dataframe


class TechnologyStudent(sim.Component):
    """
    Agente estudiante para el escenario 2: uso de tecnología educativa.

    Este escenario incorpora plataformas virtuales, materiales digitales,
    cuestionarios en línea y retroalimentación parcial.
    """

    def setup(
        self,
        state: StudentState,
        sim_config: SimulationConfig,
        scenario_config: TechnologyScenarioConfig,
    ) -> None:
        self.state = state
        self.sim_config = sim_config
        self.scenario_config = scenario_config

    def process(self):
        for _week in range(1, self.sim_config.semester_weeks + 1):
            if self.state.deserted:
                break

            self._simulate_learning_week()
            self._update_desertion_risk()
            self._check_desertion()

            self.state.weeks_completed += 1

            yield self.hold(1)

        self._finalize_student()

    def _simulate_learning_week(self) -> None:
        """
        Calcula la evolución semanal del estudiante en un entorno con tecnología.
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

        digital_resources_effect = (
            self.state.technology_score
            * cfg.digital_resources_weight
            * cfg.methodology_factor
            * 20
        )

        penalty = self._calculate_penalty()

        noise = np.random.normal(cfg.noise_mean, cfg.noise_std)

        weekly_delta = (
            study_effect
            + attendance_effect
            + motivation_effect
            + technology_effect
            + digital_resources_effect
            - penalty
            + noise
        )

        self.state.current_grade += weekly_delta / self.sim_config.semester_weeks

        self.state.current_grade = min(
            max(self.state.current_grade, self.sim_config.min_grade),
            self.sim_config.max_grade,
        )

    def _calculate_penalty(self) -> float:
        """
        Penaliza condiciones débiles.

        En este escenario, el bajo acceso tecnológico tiene mayor impacto
        que en el escenario tradicional.
        """

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
        Actualiza el riesgo de deserción.

        La tecnología reduce parcialmente el riesgo si el estudiante tiene
        acceso medio o alto, pero no elimina el problema si el rendimiento
        sigue siendo bajo.
        """

        cfg = self.scenario_config

        risk_growth = 0.0

        if self.state.current_grade < cfg.low_performance_threshold:
            risk_growth += cfg.weekly_risk_growth

        if self.state.study_hours < 4:
            risk_growth += 0.035

        if self.state.attendance < 70:
            risk_growth += 0.035

        if self.state.motivation < 0.40:
            risk_growth += 0.04

        if self.state.technology_access == "bajo":
            risk_growth += 0.04

        if risk_growth == 0.0:
            self.state.desertion_risk -= cfg.weekly_risk_reduction
        else:
            self.state.desertion_risk += risk_growth

        # Reducción parcial del riesgo por disponibilidad tecnológica.
        if self.state.technology_access == "medio":
            self.state.desertion_risk -= 0.015

        if self.state.technology_access == "alto":
            self.state.desertion_risk -= 0.025

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


class TechnologyScenario:
    """
    Escenario 2: uso de tecnología educativa.
    """

    def __init__(
        self,
        sim_config: SimulationConfig | None = None,
        scenario_config: TechnologyScenarioConfig | None = None,
        cohort: list[StudentState] | None = None,
    ) -> None:
        self.sim_config = sim_config or SimulationConfig()
        self.scenario_config = scenario_config or TechnologyScenarioConfig()
        self.students: list[StudentState] = cohort or []

    def run(self) -> dict:
        random.seed(self.sim_config.random_seed)
        np.random.seed(self.sim_config.random_seed)

        env = sim.Environment(trace=False)

        if not self.students:
            raise ValueError(
                "No se recibió una cohorte. Usa CohortFactory para generar estudiantes."
            )

        for student_state in self.students:
            TechnologyStudent(
                state=student_state,
                sim_config=self.sim_config,
                scenario_config=self.scenario_config,
            )

        env.run(till=self.sim_config.semester_weeks + 1)

        df = students_to_dataframe(self.students)
        kpis = calculate_kpis(df)

        return {
            "scenario": "Uso de tecnología educativa",
            "dataframe": df,
            "kpis": kpis,
        }

    def save_results(self, output_dir: str = "outputs/results") -> None:
        result = self.run()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        df = result["dataframe"]
        kpis = result["kpis"]

        df.to_csv(output_path / "technology_scenario_students.csv", index=False)

        kpi_df = self._kpis_to_dataframe(kpis)
        kpi_df.to_csv(output_path / "technology_scenario_kpis.csv", index=False)

    @staticmethod
    def _kpis_to_dataframe(kpis: dict) -> pd.DataFrame:
        return pd.DataFrame([kpis])
