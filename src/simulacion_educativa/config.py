from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    """
    Configuración general del escenario tradicional.
    """

    num_students: int = 100
    semester_weeks: int = 16
    passing_grade: float = 11.0
    min_grade: float = 0.0
    max_grade: float = 20.0
    random_seed: int = 42


@dataclass(frozen=True)
class TraditionalScenarioConfig:
    """
    Parámetros propios del escenario 1: educación tradicional.

    Este escenario representa:
    - clases expositivas,
    - baja personalización,
    - retroalimentación limitada,
    - uso mínimo de tecnología.
    """

    methodology_factor: float = 0.90
    feedback_factor: float = 0.40
    technology_factor: float = 0.10
    personalization_factor: float = 0.00

    # Pesos de mejora semanal
    study_weight: float = 0.055
    attendance_weight: float = 0.035
    motivation_weight: float = 0.025
    technology_weight: float = 0.010

    # Penalizaciones
    low_study_penalty: float = 0.08
    low_attendance_penalty: float = 0.10
    low_motivation_penalty: float = 0.06

    # Ruido aleatorio semanal
    noise_mean: float = 0.0
    noise_std: float = 0.18

    # Deserción
    desertion_risk_threshold: float = 0.85
    weekly_risk_growth: float = 0.045
    weekly_risk_reduction: float = 0.025
    low_performance_threshold: float = 8.0


@dataclass(frozen=True)
class TechnologyScenarioConfig:
    """
    Parámetros del escenario 2: uso de tecnología educativa.

    Este escenario representa:
    - plataformas virtuales,
    - materiales digitales,
    - cuestionarios en línea,
    - retroalimentación parcial,
    - sin IA personalizada.
    """

    methodology_factor: float = 1.00
    feedback_factor: float = 0.60
    technology_factor: float = 0.50
    personalization_factor: float = 0.10

    # Pesos de mejora semanal
    study_weight: float = 0.055
    attendance_weight: float = 0.035
    motivation_weight: float = 0.030
    technology_weight: float = 0.045
    digital_resources_weight: float = 0.035

    # Penalizaciones
    low_study_penalty: float = 0.06
    low_attendance_penalty: float = 0.08
    low_motivation_penalty: float = 0.05
    low_technology_penalty: float = 0.07

    # Ruido aleatorio semanal
    noise_mean: float = 0.0
    noise_std: float = 0.16

    # Deserción
    desertion_risk_threshold: float = 0.88
    low_performance_threshold: float = 8.0
    weekly_risk_growth: float = 0.040
    weekly_risk_reduction: float = 0.040


@dataclass(frozen=True)
class AIPersonalizedScenarioConfig:
    """
    Parámetros del escenario 3: educación personalizada con IA.

    Este escenario representa:
    - tutoría inteligente,
    - detección temprana de riesgo,
    - retroalimentación personalizada,
    - recursos adaptativos,
    - intervención según riesgo académico.
    """

    methodology_factor: float = 1.10
    feedback_factor: float = 0.90
    technology_factor: float = 0.70
    personalization_factor: float = 0.90

    # Pesos de mejora semanal
    study_weight: float = 0.060
    attendance_weight: float = 0.038
    motivation_weight: float = 0.040
    technology_weight: float = 0.055

    # Intervenciones IA
    low_risk_intervention: float = 0.04
    medium_risk_intervention: float = 0.12
    high_risk_intervention: float = 0.20
    personalization_weight: float = 0.090

    # Penalizaciones
    low_study_penalty: float = 0.04
    low_attendance_penalty: float = 0.06
    low_motivation_penalty: float = 0.04
    low_technology_penalty: float = 0.05

    # Ruido aleatorio semanal
    noise_mean: float = 0.0
    noise_std: float = 0.14

    # Deserción
    desertion_risk_threshold: float = 0.90
    low_performance_threshold: float = 8.0
    weekly_risk_growth: float = 0.035
    weekly_risk_reduction: float = 0.070
