from __future__ import annotations

import copy
import random

import numpy as np

from simulacion_educativa.config import SimulationConfig
from simulacion_educativa.entities import AccessLevel, StudentState


class CohortFactory:
    """
    Genera cohortes sintéticas de estudiantes.

    La misma cohorte puede reutilizarse en varios escenarios para hacer
    comparaciones justas entre metodologías.
    """

    def __init__(self, sim_config: SimulationConfig) -> None:
        self.sim_config = sim_config

    def create_cohort(self) -> list[StudentState]:
        """
        Crea una cohorte base usando la semilla configurada.
        """

        random.seed(self.sim_config.random_seed)
        np.random.seed(self.sim_config.random_seed)

        students = []

        for student_id in range(1, self.sim_config.num_students + 1):
            students.append(
                StudentState(
                    student_id=student_id,
                    study_hours=self._generate_study_hours(),
                    technology_access=self._generate_technology_access(),
                    attendance=self._generate_attendance(),
                    motivation=self._generate_motivation(),
                    initial_performance=self._generate_initial_performance(),
                    age=self._generate_age(),
                    gender=self._generate_gender(),
                    school_type=self._generate_school_type(),
                    parent_education=self._generate_parent_education(),
                    travel_time=self._generate_travel_time(),
                    extra_activities=self._generate_extra_activities(),
                    study_method=self._generate_study_method(),
                )
            )

        return students

    @staticmethod
    def clone_cohort(cohort: list[StudentState]) -> list[StudentState]:
        """
        Crea una copia profunda de la cohorte.

        Esto evita que un escenario modifique los resultados del otro.
        """
        return copy.deepcopy(cohort)

    @staticmethod
    def _generate_study_hours() -> float:
        """
        Genera horas de estudio semanales.
        """
        value = np.random.normal(loc=7.0, scale=3.0)
        return round(float(min(max(value, 0.0), 20.0)), 2)

    @staticmethod
    def _generate_technology_access() -> AccessLevel:
        """
        Genera nivel de acceso tecnológico.
        """
        return random.choices(
            population=["bajo", "medio", "alto"],
            weights=[0.25, 0.45, 0.30],
            k=1,
        )[0]

    @staticmethod
    def _generate_attendance() -> float:
        """
        Genera porcentaje de asistencia.
        """
        value = np.random.normal(loc=78.0, scale=12.0)
        return round(float(min(max(value, 40.0), 100.0)), 2)

    @staticmethod
    def _generate_motivation() -> float:
        """
        Genera motivación entre 0 y 1.
        """
        value = np.random.normal(loc=0.62, scale=0.20)
        return round(float(min(max(value, 0.0), 1.0)), 2)

    @staticmethod
    def _generate_initial_performance() -> float:
        """
        Genera rendimiento inicial en escala de 0 a 20.
        """
        value = np.random.normal(loc=10.5, scale=2.2)
        return round(float(min(max(value, 0.0), 20.0)), 2)

    @staticmethod
    def _generate_age() -> int:
        return int(
            np.random.choice([17, 18, 19, 20, 21], p=[0.10, 0.35, 0.30, 0.15, 0.10])
        )

    @staticmethod
    def _generate_gender() -> str:
        return random.choice(["male", "female"])

    @staticmethod
    def _generate_school_type() -> str:
        return random.choices(
            population=["public", "private"],
            weights=[0.65, 0.35],
            k=1,
        )[0]

    @staticmethod
    def _generate_parent_education() -> str:
        return random.choices(
            population=["none", "high school", "bachelor", "master"],
            weights=[0.10, 0.50, 0.30, 0.10],
            k=1,
        )[0]

    @staticmethod
    def _generate_travel_time() -> str:
        return random.choices(
            population=["<30 min", "30-60 min", ">60 min"],
            weights=[0.35, 0.45, 0.20],
            k=1,
        )[0]

    @staticmethod
    def _generate_extra_activities() -> str:
        return random.choices(
            population=["yes", "no"],
            weights=[0.40, 0.60],
            k=1,
        )[0]

    @staticmethod
    def _generate_study_method() -> str:
        return random.choices(
            population=["notes", "videos", "group study", "practice tests"],
            weights=[0.35, 0.25, 0.20, 0.20],
            k=1,
        )[0]
