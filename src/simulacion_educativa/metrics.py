from __future__ import annotations

from typing import Iterable

import pandas as pd

from simulacion_educativa.entities import StudentState


def students_to_dataframe(students: Iterable[StudentState]) -> pd.DataFrame:
    """
    Convierte los resultados individuales de estudiantes a DataFrame.
    """

    rows = []

    for student in students:
        rows.append(
            {
                "student_id": student.student_id,
                "study_hours": student.study_hours,
                "technology_access": student.technology_access,
                "attendance": student.attendance,
                "motivation": student.motivation,
                "initial_performance": student.initial_performance,
                "final_grade": student.final_grade,
                "approved": student.approved,
                "deserted": student.deserted,
                "desertion_risk": student.desertion_risk,
                "weeks_completed": student.weeks_completed,
                "ml_risk_probability": student.ml_risk_probability,
                "ml_risk_level": student.ml_risk_level,
                "age": student.age,
                "gender": student.gender,
                "school_type": student.school_type,
                "parent_education": student.parent_education,
                "travel_time": student.travel_time,
                "extra_activities": student.extra_activities,
                "study_method": student.study_method,
            }
        )

    return pd.DataFrame(rows)


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula indicadores agregados del escenario.
    """

    total_students = len(df)

    if total_students == 0:
        raise ValueError("No hay estudiantes para calcular KPIs.")

    approved_count = int(df["approved"].sum())
    deserted_count = int(df["deserted"].sum())
    active_finished_count = total_students - deserted_count
    failed_count = total_students - approved_count - deserted_count

    approval_rate = (approved_count / total_students) * 100
    failure_rate = (failed_count / total_students) * 100
    desertion_rate = (deserted_count / total_students) * 100

    if active_finished_count > 0:
        approval_rate_non_deserted = (approved_count / active_finished_count) * 100
        failure_rate_non_deserted = (failed_count / active_finished_count) * 100
    else:
        approval_rate_non_deserted = 0.0
        failure_rate_non_deserted = 0.0

    return {
        "total_students": total_students,
        "average_final_grade": round(float(df["final_grade"].mean()), 2),
        "approval_rate": round(approval_rate, 2),
        "failure_rate": round(failure_rate, 2),
        "desertion_rate": round(desertion_rate, 2),
        "approval_rate_non_deserted": round(approval_rate_non_deserted, 2),
        "failure_rate_non_deserted": round(failure_rate_non_deserted, 2),
        "average_desertion_risk": round(float(df["desertion_risk"].mean()), 2),
    }
