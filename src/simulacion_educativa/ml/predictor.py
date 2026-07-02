from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


class RiskPredictor:
    """
    Carga el modelo entrenado y permite predecir riesgo académico.

    Salida:
    - risk_academic = 1 significa riesgo alto de desaprobación.
    - risk_academic = 0 significa bajo riesgo.
    """

    def __init__(
        self,
        model_path: str = "outputs/models/best_risk_model.joblib",
    ) -> None:
        path = Path(model_path)

        if not path.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo en: {path}. "
                "Primero ejecuta: uv run python -m simulacion_educativa.ml.train_model"
            )

        self.model = joblib.load(path)

    def predict_risk(self, student_data: dict) -> int:
        df = pd.DataFrame([student_data])
        prediction = self.model.predict(df)[0]

        return int(prediction)

    def predict_risk_probability(self, student_data: dict) -> float:
        df = pd.DataFrame([student_data])
        probabilities = self.model.predict_proba(df)[0]
        classes = list(self.model.classes_)

        risk_index = classes.index(1)

        return float(probabilities[risk_index])

    def classify_risk_level(self, student_data: dict) -> str:
        probability = self.predict_risk_probability(student_data)

        if probability >= 0.70:
            return "alto"

        if probability >= 0.40:
            return "medio"

        return "bajo"
