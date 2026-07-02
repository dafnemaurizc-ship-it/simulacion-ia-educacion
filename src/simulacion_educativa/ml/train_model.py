from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from simulacion_educativa.ml.preprocessing import MLConfig, prepare_dataset


def build_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str],
) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )


def build_model_pipeline(
    model: BaseEstimator,
    numeric_features: list[str],
    categorical_features: list[str],
) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(
                    numeric_features=numeric_features,
                    categorical_features=categorical_features,
                ),
            ),
            ("model", model),
        ]
    )


def get_models(random_seed: int = 42) -> dict[str, BaseEstimator]:
    """
    Modelos a comparar.

    La clase positiva es:
    risk_academic = 1
    """

    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=random_seed,
        ),
        "decision_tree": DecisionTreeClassifier(
            max_depth=6,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=random_seed,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=random_seed,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=random_seed,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=random_seed,
        ),
        "knn": KNeighborsClassifier(
            n_neighbors=7,
            weights="distance",
        ),
        "svm_rbf": SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            class_weight="balanced",
            probability=True,
            random_state=random_seed,
        ),
        "gaussian_naive_bayes": GaussianNB(),
    }


def evaluate_model(model: Pipeline, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(
            y_test,
            y_pred,
            zero_division=0,
            output_dict=True,
        ),
    }

    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
        metrics["roc_auc"] = round(float(roc_auc_score(y_test, y_proba)), 4)
    else:
        metrics["roc_auc"] = None

    return metrics


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def select_best_model(comparison_df: pd.DataFrame) -> str:
    """
    Selecciona el mejor modelo priorizando F1.

    Para este caso, F1 es más útil que accuracy porque interesa detectar
    estudiantes en riesgo sin ignorar falsos negativos.
    """

    sorted_df = comparison_df.sort_values(
        by=["f1", "recall", "roc_auc", "precision"],
        ascending=False,
    )

    return str(sorted_df.iloc[0]["model_key"])


def train_models() -> None:
    config = MLConfig()

    X, y, numeric_features, categorical_features = prepare_dataset(config)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_seed,
        stratify=y,
    )

    output_models = Path("outputs/models")
    output_metrics = Path("outputs/metrics")
    output_models.mkdir(parents=True, exist_ok=True)
    output_metrics.mkdir(parents=True, exist_ok=True)

    models = get_models(random_seed=config.random_seed)

    results = []
    trained_pipelines: dict[str, Pipeline] = {}

    for model_key, estimator in models.items():
        print(f"\nEntrenando modelo: {model_key}")

        pipeline = build_model_pipeline(
            model=estimator,
            numeric_features=numeric_features,
            categorical_features=categorical_features,
        )

        pipeline.fit(X_train, y_train)

        metrics = evaluate_model(pipeline, X_test, y_test)

        trained_pipelines[model_key] = pipeline

        joblib.dump(
            pipeline,
            output_models / f"{model_key}_risk_model.joblib",
        )

        save_json(
            metrics,
            output_metrics / f"{model_key}_risk_model_metrics.json",
        )

        results.append(
            {
                "model_key": model_key,
                "accuracy": metrics["accuracy"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "roc_auc": metrics["roc_auc"],
            }
        )

    comparison_df = pd.DataFrame(results)

    comparison_df = comparison_df.sort_values(
        by=["f1", "recall", "roc_auc", "precision"],
        ascending=False,
    )

    comparison_df.to_csv(
        output_metrics / "model_comparison.csv",
        index=False,
    )

    best_model_key = select_best_model(comparison_df)
    best_model = trained_pipelines[best_model_key]

    joblib.dump(
        best_model,
        output_models / "best_risk_model.joblib",
    )

    best_summary = {
        "best_model_key": best_model_key,
        "selection_criteria": "Mayor F1, luego recall, luego roc_auc, luego precision",
        "target": config.target_column,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
    }

    save_json(
        best_summary,
        output_metrics / "best_model_summary.json",
    )

    print("\n=== COMPARACIÓN DE MODELOS ===\n")
    print(comparison_df)

    print("\n=== MEJOR MODELO SELECCIONADO ===\n")
    print(best_model_key)

    print("\nModelo operativo guardado en:")
    print(output_models / "best_risk_model.joblib")


if __name__ == "__main__":
    train_models()
