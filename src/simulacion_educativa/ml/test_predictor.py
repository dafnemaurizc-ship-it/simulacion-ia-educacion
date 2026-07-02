from simulacion_educativa.ml.predictor import RiskPredictor


def main() -> None:
    predictor = RiskPredictor()

    student = {
        "age": 17,
        "study_hours": 3.0,
        "attendance_percentage": 65.0,
        "gender": "male",
        "school_type": "public",
        "parent_education": "high school",
        "internet_access": "no",
        "travel_time": ">60 min",
        "extra_activities": "no",
        "study_method": "notes",
    }

    risk_class = predictor.predict_risk(student)
    risk_probability = predictor.predict_risk_probability(student)
    risk_level = predictor.classify_risk_level(student)

    print("\n=== PREDICCIÓN DE RIESGO ===\n")
    print(f"Clase de riesgo: {risk_class}")
    print(f"Probabilidad de riesgo: {risk_probability:.2f}")
    print(f"Nivel de riesgo: {risk_level}")


if __name__ == "__main__":
    main()
