from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import salabim as sim

from simulacion_educativa.config import (
    SimulationConfig,
    TraditionalScenarioConfig,
)
from simulacion_educativa.entities import AccessLevel, StudentState
from simulacion_educativa.metrics import calculate_kpis, students_to_dataframe


class Student(sim.Component):
    """
    Agente estudiante para el escenario tradicional.

    En salabim, cada estudiante es un componente que ejecuta su propio proceso
    durante las semanas del semestre.
    """

    def setup(
        self,
        state: StudentState,
        sim_config: SimulationConfig,
        scenario_config: TraditionalScenarioConfig,
    ) -> None:
        self.state = state
        self.sim_config = sim_config
        self.scenario_config = scenario_config

    def process(self):
        """
        Proceso principal del estudiante durante el semestre.
        """

        for _week in range(1, self.sim_config.semester_weeks + 1):
            if self.state.deserted:
                break

            self._simulate_learning_week()
            self._update_desertion_risk()
            self._check_desertion()

            self.state.weeks_completed += 1

            # Una semana simulada.
            yield self.hold(1)

        self._finalize_student()

    def _simulate_learning_week(self) -> None:
        """
        Calcula la evolución del rendimiento semanal.
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

        penalty = self._calculate_penalty()

        noise = np.random.normal(cfg.noise_mean, cfg.noise_std)

        weekly_delta = (
            study_effect
            + attendance_effect
            + motivation_effect
            + technology_effect
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
        Penaliza condiciones débiles en el escenario tradicional.
        """

        cfg = self.scenario_config
        penalty = 0.0

        if self.state.study_hours < 4:
            penalty += cfg.low_study_penalty

        if self.state.attendance < 70:
            penalty += cfg.low_attendance_penalty

        if self.state.motivation < 0.40:
            penalty += cfg.low_motivation_penalty

        return penalty

    def _update_desertion_risk(self) -> None:
        """
        Actualiza el riesgo de deserción.

        En el escenario tradicional, el riesgo sube cuando hay:
        - bajo rendimiento,
        - baja motivación,
        - pocas horas de estudio,
        - baja asistencia.
        """

        cfg = self.scenario_config

        risk_growth = 0.0

        if self.state.current_grade < cfg.low_performance_threshold:
            risk_growth += cfg.weekly_risk_growth

        if self.state.study_hours < 4:
            risk_growth += 0.04

        if self.state.attendance < 70:
            risk_growth += 0.04

        if self.state.motivation < 0.40:
            risk_growth += 0.05

        if risk_growth == 0.0:
            self.state.desertion_risk -= cfg.weekly_risk_reduction
        else:
            self.state.desertion_risk += risk_growth

        self.state.desertion_risk = min(max(self.state.desertion_risk, 0.0), 1.0)

    def _check_desertion(self) -> None:
        """
        Determina si el estudiante deserta.
        """

        cfg = self.scenario_config

        if self.state.desertion_risk >= cfg.desertion_risk_threshold:
            self.state.deserted = True

    def _finalize_student(self) -> None:
        """
        Cierra el estado final del estudiante.
        """

        self.state.final_grade = round(self.state.current_grade, 2)

        if self.state.deserted:
            self.state.approved = False
            return

        self.state.approved = self.state.final_grade >= self.sim_config.passing_grade


class TraditionalScenario:
    """
    Escenario 1: educación tradicional.
    """

    def __init__(
        self,
        sim_config: SimulationConfig | None = None,
        scenario_config: TraditionalScenarioConfig | None = None,
        cohort: list[StudentState] | None = None,
    ) -> None:
        self.sim_config = sim_config or SimulationConfig()
        self.scenario_config = scenario_config or TraditionalScenarioConfig()
        self.students: list[StudentState] = cohort or []

    def run(self) -> dict:
        """
        Ejecuta la simulación completa.
        """

        random.seed(self.sim_config.random_seed)
        np.random.seed(self.sim_config.random_seed)

        env = sim.Environment(trace=False)

        if not self.students:
            raise ValueError(
                "No se recibió una cohorte. Usa CohortFactory para generar estudiantes."
            )

        for student_state in self.students:
            Student(
                state=student_state,
                sim_config=self.sim_config,
                scenario_config=self.scenario_config,
            )

        env.run(till=self.sim_config.semester_weeks + 1)

        df = students_to_dataframe(self.students)
        kpis = calculate_kpis(df)

        return {
            "scenario": "Educación tradicional",
            "dataframe": df,
            "kpis": kpis,
        }

    def save_results(self, output_dir: str = "outputs/results") -> None:
        """
        Guarda resultados en CSV.

        Importante: esta función ya no vuelve a ejecutar la simulación.
        Se recomienda pasarle resultados ya ejecutados desde main.py.
        """

        result = self.run()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        df = result["dataframe"]
        kpis = result["kpis"]

        df.to_csv(output_path / "traditional_scenario_students.csv", index=False)

        kpi_df = self._kpis_to_dataframe(kpis)
        kpi_df.to_csv(output_path / "traditional_scenario_kpis.csv", index=False)

    @staticmethod
    def _kpis_to_dataframe(kpis: dict):
        import pandas as pd

        return pd.DataFrame([kpis])
