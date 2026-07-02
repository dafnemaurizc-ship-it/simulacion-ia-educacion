from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class MLConfig:
    """
    Configuración del modelo de machine learning.

    La variable objetivo será risk_academic:
    - 1 = estudiante en riesgo académico
    - 0 = estudiante sin riesgo académico
    """

    dataset_path: str = "data/Student_Performance.csv"
    target_column: str = "risk_academic"
    approval_threshold_20: float = 11.0
    random_seed: int = 42
    test_size: float = 0.20


NUMERIC_FEATURES = [
    "age",
    "study_hours",
    "attendance_percentage",
]

CATEGORICAL_FEATURES = [
    "gender",
    "school_type",
    "parent_education",
    "internet_access",
    "travel_time",
    "extra_activities",
    "study_method",
]

EXCLUDED_COLUMNS = [
    "student_id",
    "math_score",
    "science_score",
    "english_score",
    "overall_score",
    "final_grade",
    "risk_academic",
    "approved",
    "score_20",
]


def load_dataset(dataset_path: str) -> pd.DataFrame:
    """
    Carga el dataset desde CSV.
    """

    path = Path(dataset_path)

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en: {path}. "
            "Coloca el archivo como data/Student_Performance.csv"
        )

    return pd.read_csv(path)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza nombres de columnas a snake_case básico.
    """

    df = df.copy()
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_")
    )
    return df


def create_target(
    df: pd.DataFrame, approval_threshold_20: float = 11.0
) -> pd.DataFrame:
    """
    Crea variables objetivo.

    El dataset tiene overall_score en escala 0-100.
    Para adaptarlo a la escala peruana de 0-20:

        score_20 = overall_score / 5

    Luego:
        approved = 1 si score_20 >= 11
        risk_academic = 1 si score_20 < 11
    """

    df = df.copy()

    if "overall_score" not in df.columns:
        raise ValueError("El dataset debe contener la columna overall_score.")

    df["score_20"] = df["overall_score"] / 5.0
    df["approved"] = (df["score_20"] >= approval_threshold_20).astype(int)
    df["risk_academic"] = (df["approved"] == 0).astype(int)

    return df


def get_feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """
    Devuelve las variables numéricas y categóricas realmente disponibles.
    """

    numeric_features = [col for col in NUMERIC_FEATURES if col in df.columns]
    categorical_features = [col for col in CATEGORICAL_FEATURES if col in df.columns]

    return numeric_features, categorical_features


def split_features_target(
    df: pd.DataFrame,
    target_column: str = "risk_academic",
) -> tuple[pd.DataFrame, pd.Series, list[str], list[str]]:
    """
    Separa X, y y lista de columnas útiles.
    """

    if target_column not in df.columns:
        raise ValueError(f"No existe la variable objetivo: {target_column}")

    numeric_features, categorical_features = get_feature_columns(df)

    selected_features = numeric_features + categorical_features

    if not selected_features:
        raise ValueError("No se encontraron variables predictoras válidas.")

    X = df[selected_features].copy()
    y = df[target_column].copy()

    return X, y, numeric_features, categorical_features


def prepare_dataset(
    config: MLConfig,
) -> tuple[pd.DataFrame, pd.Series, list[str], list[str]]:
    """
    Pipeline completo de carga y preparación del dataset.
    """

    df = load_dataset(config.dataset_path)
    df = normalize_column_names(df)
    df = create_target(df, approval_threshold_20=config.approval_threshold_20)

    return split_features_target(df, target_column=config.target_column)
