from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import salabim as sim

from simulacion_educativa.visualization.runtime import build_environment
from simulacion_educativa.visualization.styles import (
    CARD_ACCENT,
    CARD_FILL,
    FINAL_ACCENT,
    FINAL_BG,
    FINAL_CARD_BORDER,
    FINAL_CARD_FILL,
    HEADER_BG,
    HEADER_HEIGHT,
    PROGRESS_BG,
    PROGRESS_BORDER,
    PROGRESS_FILL,
    TEXT_FILL,
    TEXT_MUTED,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


@dataclass(slots=True)
class ScenarioSummary:
    key: str
    name: str
    average_final_grade: float
    approval_rate: float
    failure_rate: float
    desertion_rate: float
    approval_rate_non_deserted: float
    average_desertion_risk: float
    total_students: int


def build_summary_frame(results: list[dict]) -> pd.DataFrame:
    rows = []

    for result in results:
        rows.append(
            {
                "scenario": result["scenario"],
                **result["kpis"],
            }
        )

    return pd.DataFrame(rows)


def _winner_label(summaries: list[ScenarioSummary]) -> dict[str, ScenarioSummary]:
    return {
        "approval": max(summaries, key=lambda item: item.approval_rate),
        "grade": max(summaries, key=lambda item: item.average_final_grade),
        "retention": min(summaries, key=lambda item: item.desertion_rate),
    }


def show_final_dashboard(
    results: list[dict],
    selected_scenes: list[str],
    *,
    speed: float = 1.0,
) -> None:
    if not results:
        return

    if not sim.can_animate():
        print("\n=== DASHBOARD FINAL ===\n")
        print(build_summary_frame(results))
        return

    env = build_environment(
        animate=True,
        title="Dashboard final",
        speed=speed,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
    )

    summaries = [
        ScenarioSummary(
            key=result["key"],
            name=result["scenario"],
            average_final_grade=result["kpis"]["average_final_grade"],
            approval_rate=result["kpis"]["approval_rate"],
            failure_rate=result["kpis"]["failure_rate"],
            desertion_rate=result["kpis"]["desertion_rate"],
            approval_rate_non_deserted=result["kpis"]["approval_rate_non_deserted"],
            average_desertion_risk=result["kpis"]["average_desertion_risk"],
            total_students=result["kpis"]["total_students"],
        )
        for result in results
    ]
    winners = _winner_label(summaries)

    class DashboardHold(sim.Component):
        def setup(self) -> None:
            self._build_scene()

        def process(self):
            yield self.hold(4)

        def _build_scene(self) -> None:
            sim.AnimateRectangle(
                spec=(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
                fillcolor=FINAL_BG,
                linecolor=FINAL_BG,
                linewidth=0,
                env=env,
            )
            sim.AnimateRectangle(
                spec=(0, WINDOW_HEIGHT - HEADER_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT),
                fillcolor=HEADER_BG,
                linecolor=HEADER_BG,
                linewidth=0,
                env=env,
            )

            sim.AnimateText(
                x=44,
                y=776,
                fontsize=22,
                textcolor=TEXT_FILL,
                text="Dashboard final",
                env=env,
            )
            sim.AnimateText(
                x=44,
                y=750,
                fontsize=10,
                textcolor=TEXT_MUTED,
                text=lambda _arg, _t: "Escenas seleccionadas: " + ", ".join(selected_scenes),
                env=env,
            )

            self._metric_badge(
                x=1010,
                y=776,
                label="Mejor aprobacion",
                value=winners["approval"].name,
                color=CARD_ACCENT,
            )
            self._metric_badge(
                x=1010,
                y=744,
                label="Menor desercion",
                value=winners["retention"].name,
                color=FINAL_ACCENT,
            )
            self._metric_badge(
                x=1010,
                y=712,
                label="Mejor promedio",
                value=winners["grade"].name,
                color="#f59e0b",
            )

            card_gap = 18
            top = 682
            usable_width = WINDOW_WIDTH - 88
            columns = 1 if len(summaries) == 1 else 2 if len(summaries) == 2 else 3
            card_width = (usable_width - card_gap * (columns - 1)) / columns
            card_height = 322

            for index, summary in enumerate(summaries):
                column = index % columns
                row = index // columns
                x = 44 + (column * (card_width + card_gap))
                y_top = top - (row * (card_height + 14))
                self._summary_card(summary, x, y_top, card_width, card_height)

            self._footer()

        def _metric_badge(self, x: float, y: float, label: str, value: str, color: str) -> None:
            sim.AnimateRectangle(
                spec=(x, y - 22, x + 314, y + 8),
                fillcolor=CARD_FILL,
                linecolor=color,
                linewidth=1,
                env=env,
            )
            sim.AnimateText(
                x=x + 16,
                y=y - 4,
                fontsize=10,
                textcolor=TEXT_MUTED,
                text=f"{label}",
                env=env,
            )
            sim.AnimateText(
                x=x + 168,
                y=y - 4,
                fontsize=10,
                textcolor=TEXT_FILL,
                text=value,
                env=env,
            )

        def _summary_card(self, summary: ScenarioSummary, x: float, y_top: float, width: float, height: float) -> None:
            sim.AnimateRectangle(
                spec=(x, y_top - height, x + width, y_top),
                fillcolor=FINAL_CARD_FILL,
                linecolor=FINAL_CARD_BORDER,
                linewidth=1,
                env=env,
            )

            sim.AnimateText(
                x=x + 22,
                y=y_top - 28,
                fontsize=15,
                textcolor=TEXT_FILL,
                text=summary.name,
                env=env,
            )
            sim.AnimateText(
                x=x + 22,
                y=y_top - 52,
                fontsize=9,
                textcolor=TEXT_MUTED,
                text=lambda _arg, _t, s=summary: f"{s.total_students} estudiantes | {s.key}",
                env=env,
            )

            self._bar(
                x + 22,
                y_top - 86,
                width - 44,
                "Aprobacion",
                summary.approval_rate,
                "#22c55e",
            )
            self._bar(
                x + 22,
                y_top - 144,
                width - 44,
                "Desercion",
                summary.desertion_rate,
                "#ef4444",
            )

            self._stat_pair(x + 22, y_top - 206, "Promedio final", f"{summary.average_final_grade:.2f}")
            self._stat_pair(x + 22, y_top - 238, "Riesgo medio", f"{summary.average_desertion_risk:.2f}")
            self._stat_pair(x + 22, y_top - 270, "Aprobados sin desertar", f"{summary.approval_rate_non_deserted:.2f}%")
            self._stat_pair(x + 22, y_top - 302, "Fallos", f"{summary.failure_rate:.2f}%")

        def _bar(self, x: float, y: float, width: float, label: str, value: float, color: str) -> None:
            sim.AnimateText(
                x=x,
                y=y + 18,
                fontsize=9,
                textcolor=TEXT_MUTED,
                text=f"{label}: {value:.2f}%",
                env=env,
            )
            sim.AnimateRectangle(
                spec=(x, y - 2, x + width, y + 12),
                fillcolor=PROGRESS_BG,
                linecolor=PROGRESS_BORDER,
                linewidth=1,
                env=env,
            )
            sim.AnimateRectangle(
                spec=lambda _arg, _t, w=width, v=value, xx=x, yy=y: (
                    xx,
                    yy - 2,
                    xx + (w * max(0.0, min(v, 100.0)) / 100.0),
                    yy + 12,
                ),
                fillcolor=color,
                linecolor=color,
                linewidth=1,
                env=env,
            )

        def _stat_pair(self, x: float, y: float, label: str, value: str) -> None:
            sim.AnimateText(
                x=x,
                y=y,
                fontsize=9,
                textcolor=TEXT_MUTED,
                text=label,
                env=env,
            )
            sim.AnimateText(
                x=x + 250,
                y=y,
                fontsize=10,
                textcolor=TEXT_FILL,
                text=value,
                env=env,
            )

        def _footer(self) -> None:
            sim.AnimateText(
                x=44,
                y=20,
                fontsize=10,
                textcolor=TEXT_MUTED,
                text="Comparacion construida con la cohorte base clonada para cada escena.",
                env=env,
            )

    dashboard = DashboardHold(env=env)
    dashboard.activate()
    env.run(till=4)
