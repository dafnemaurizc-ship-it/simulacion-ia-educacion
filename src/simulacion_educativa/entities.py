from dataclasses import dataclass, field
from typing import Literal

AccessLevel = Literal["bajo", "medio", "alto"]


@dataclass
class StudentState:
    """
    Estado individual de cada estudiante dentro de la simulación.
    """

    student_id: int
    study_hours: float
    technology_access: AccessLevel
    attendance: float
    motivation: float
    initial_performance: float

    # Variables adicionales para el modelo ML
    age: int = 18
    gender: str = "male"
    school_type: str = "public"
    parent_education: str = "high school"
    travel_time: str = "30-60 min"
    extra_activities: str = "no"
    study_method: str = "notes"

    current_grade: float = field(init=False)
    final_grade: float = field(default=0.0)
    desertion_risk: float = field(default=0.0)
    deserted: bool = field(default=False)
    approved: bool = field(default=False)
    weeks_completed: int = field(default=0)

    # Resultado ML
    ml_risk_probability: float = field(default=0.0)
    ml_risk_level: str = field(default="bajo")

    def __post_init__(self) -> None:
        self.current_grade = self.initial_performance

    @property
    def technology_score(self) -> float:
        values = {
            "bajo": 0.30,
            "medio": 0.60,
            "alto": 1.00,
        }
        return values[self.technology_access]

    @property
    def internet_access_for_ml(self) -> str:
        """
        Convierte acceso tecnológico de la simulación al formato del modelo ML.
        """
        if self.technology_access == "bajo":
            return "no"
        return "yes"

    @property
    def normalized_study_hours(self) -> float:
        return min(self.study_hours / 20.0, 1.0)

    @property
    def normalized_attendance(self) -> float:
        return min(max(self.attendance / 100.0, 0.0), 1.0)

    @property
    def normalized_motivation(self) -> float:
        return min(max(self.motivation, 0.0), 1.0)

    def visual_risk_level(self) -> str:
        if self.desertion_risk < 0.33:
            return "bajo"

        if self.desertion_risk < 0.66:
            return "medio"

        return "alto"

    def visual_status(self) -> str:
        if self.deserted:
            return "deserted"

        if self.approved:
            return "approved"

        return "active"

    def to_ml_features(self) -> dict:
        """
        Convierte el estudiante simulado al formato esperado por el modelo ML.
        """

        return {
            "age": self.age,
            "study_hours": self.study_hours,
            "attendance_percentage": self.attendance,
            "gender": self.gender,
            "school_type": self.school_type,
            "parent_education": self.parent_education,
            "internet_access": self.internet_access_for_ml,
            "travel_time": self.travel_time,
            "extra_activities": self.extra_activities,
            "study_method": self.study_method,
        }
