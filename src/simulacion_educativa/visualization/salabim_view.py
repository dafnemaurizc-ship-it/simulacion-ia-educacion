from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

import salabim as sim

from simulacion_educativa.entities import StudentState
from simulacion_educativa.visualization.styles import (
    BACKGROUND_FILL,
    CARD_ACCENT,
    CARD_FILL,
    GRID_COLUMNS,
    GRID_FILL,
    GRID_START_X,
    GRID_START_Y,
    GRID_TILE_H,
    GRID_TILE_W,
    GRID_X_GAP,
    GRID_Y_GAP,
    HEADER_BG,
    HEADER_HEIGHT,
    LEFT_PANEL_H,
    LEFT_PANEL_W,
    LEFT_PANEL_X,
    LEFT_PANEL_Y,
    PANEL_BORDER,
    PANEL_FILL,
    PROGRESS_BG,
    PROGRESS_BORDER,
    PROGRESS_FILL,
    RIGHT_PANEL_W,
    RIGHT_PANEL_X,
    RIGHT_PANEL_Y,
    RISK_BORDER,
    RISK_FILL,
    RISK_LABELS,
    STATUS_BORDER,
    STATUS_FILL,
    TECH_ACCESS_BORDER,
    TECH_ACCESS_FILL,
    TEXT_FILL,
    TEXT_MUTED,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


@dataclass(slots=True)
class _KpiSnapshot:
    average_grade: float
    average_risk: float
    approved: int
    deserted: int
    active: int
    ml_high: int = 0


class SalabimLiveView:
    def __init__(
        self,
        env: sim.Environment,
        students: list[StudentState],
        scenario_name: str,
        semester_weeks: int,
        *,
        show_ml_metrics: bool = False,
    ) -> None:
        self.env = env
        self.students = students
        self.scenario_name = scenario_name
        self.semester_weeks = semester_weeks
        self.show_ml_metrics = show_ml_metrics

        self._build_scene()

    def _build_scene(self) -> None:
        self._draw_background()
        self._draw_header()
        self._draw_student_grid()
        self._draw_sidebar()
        self._draw_footer()

    def _draw_background(self) -> None:
        sim.AnimateRectangle(
            spec=(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            fillcolor=BACKGROUND_FILL,
            linecolor=BACKGROUND_FILL,
            linewidth=0,
            env=self.env,
        )

        sim.AnimateRectangle(
            spec=(0, WINDOW_HEIGHT - HEADER_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT),
            fillcolor=HEADER_BG,
            linecolor=HEADER_BG,
            linewidth=0,
            env=self.env,
        )

        sim.AnimateRectangle(
            spec=(LEFT_PANEL_X, LEFT_PANEL_Y, LEFT_PANEL_X + LEFT_PANEL_W, LEFT_PANEL_Y + LEFT_PANEL_H),
            fillcolor=GRID_FILL,
            linecolor=PANEL_BORDER,
            linewidth=2,
            env=self.env,
        )

        sim.AnimateRectangle(
            spec=(RIGHT_PANEL_X, RIGHT_PANEL_Y, RIGHT_PANEL_X + RIGHT_PANEL_W, RIGHT_PANEL_Y + LEFT_PANEL_H),
            fillcolor=PANEL_FILL,
            linecolor=PANEL_BORDER,
            linewidth=2,
            env=self.env,
        )

    def _draw_header(self) -> None:
        sim.AnimateText(
            x=44,
            y=776,
            fontsize=24,
            textcolor=TEXT_FILL,
            text=f"{self.scenario_name}",
            env=self.env,
        )
        sim.AnimateText(
            x=44,
            y=748,
            fontsize=10,
            textcolor=TEXT_MUTED,
            text="Relleno = acceso tecnologico | borde = riesgo academico | texto = estado",
            env=self.env,
        )

        self._status_chip(
            x=1038,
            y=776,
            label="Modo",
            value="ANIMACION EN VIVO",
            color=CARD_ACCENT,
        )

        self._status_chip(
            x=1038,
            y=748,
            label="Semana",
            value=lambda: f"{int(self.env.now())}/{self.semester_weeks}",
            color=PROGRESS_FILL,
        )

        self._progress_bar()

    def _progress_bar(self) -> None:
        sim.AnimateText(
            x=44,
            y=726,
            fontsize=10,
            textcolor=TEXT_MUTED,
            text="Progreso del semestre",
            env=self.env,
        )

        sim.AnimateRectangle(
            spec=(44, 704, 1010, 720),
            fillcolor=PROGRESS_BG,
            linecolor=PROGRESS_BORDER,
            linewidth=1,
            env=self.env,
        )
        sim.AnimateRectangle(
            spec=lambda _arg, _t, self=self: (
                44,
                704,
                44 + (966 * self._progress_ratio()),
                720,
            ),
            fillcolor=PROGRESS_FILL,
            linecolor=PROGRESS_FILL,
            linewidth=1,
            env=self.env,
        )
        sim.AnimateText(
            x=1018,
            y=726,
            fontsize=10,
            textcolor=TEXT_MUTED,
            text=lambda _arg, _t, self=self: f"{self._progress_ratio() * 100:.0f}%",
            env=self.env,
        )

    def _draw_student_grid(self) -> None:
        for index, student in enumerate(self.students):
            row = index // GRID_COLUMNS
            col = index % GRID_COLUMNS
            x = GRID_START_X + (col * GRID_X_GAP)
            y = GRID_START_Y - (row * GRID_Y_GAP)

            sim.AnimateRectangle(
                spec=(x, y - GRID_TILE_H, x + GRID_TILE_W, y),
                fillcolor=self._student_fill(student),
                linecolor=self._student_border(student),
                linewidth=2,
                env=self.env,
            )
            sim.AnimateText(
                x=x + GRID_TILE_W / 2,
                y=y - 16,
                fontsize=10,
                textcolor=TEXT_FILL,
                text_anchor="c",
                text=lambda _arg, _t, s=student: self._student_tile_text(s),
                env=self.env,
            )

    def _draw_sidebar(self) -> None:
        snapshot = self._snapshot()
        cards = [
            ("Promedio final", f"{snapshot.average_grade:.2f}", "", CARD_ACCENT),
            ("Riesgo medio", f"{snapshot.average_risk:.2f}", "0..1", self._risk_accent(snapshot.average_risk)),
            ("Aprobados", str(snapshot.approved), f"{snapshot.approved / max(1, len(self.students)) * 100:.1f}%", "#22c55e"),
            ("Desertores", str(snapshot.deserted), f"{snapshot.deserted / max(1, len(self.students)) * 100:.1f}%", "#ef4444"),
            ("Activos", str(snapshot.active), "en curso", "#60a5fa"),
        ]

        if self.show_ml_metrics:
            cards.append(("Riesgo ML alto", str(snapshot.ml_high), "estudiantes", "#f59e0b"))

        sim.AnimateText(
            x=1042,
            y=664,
            fontsize=16,
            textcolor=TEXT_FILL,
            text="Panel de control",
            env=self.env,
        )

        sim.AnimateText(
            x=1042,
            y=640,
            fontsize=10,
            textcolor=TEXT_MUTED,
            text="Resumen operativo de la cohorte",
            env=self.env,
        )

        y = 612
        for label, value, detail, accent in cards:
            self._metric_card(1034, y, 290, 54, label, value, detail, accent)
            y -= 66

        self._legend()

    def _legend(self) -> None:
        sim.AnimateText(
            x=1042,
            y=208,
            fontsize=14,
            textcolor=TEXT_FILL,
            text="Leyenda",
            env=self.env,
        )

        legend_items = [
            ("Bajo acceso", TECH_ACCESS_FILL["bajo"], TECH_ACCESS_BORDER["bajo"], 176),
            ("Medio acceso", TECH_ACCESS_FILL["medio"], TECH_ACCESS_BORDER["medio"], 146),
            ("Alto acceso", TECH_ACCESS_FILL["alto"], TECH_ACCESS_BORDER["alto"], 116),
            ("Riesgo alto", RISK_FILL["alto"], RISK_BORDER["alto"], 86),
            ("Aprobado", STATUS_FILL["approved"], STATUS_BORDER["approved"], 56),
            ("Desertor", STATUS_FILL["deserted"], STATUS_BORDER["deserted"], 26),
        ]

        for label, fill, border, y in legend_items:
            sim.AnimateRectangle(
                spec=(1042, y - 10, 1068, y + 8),
                fillcolor=fill,
                linecolor=border,
                linewidth=2,
                env=self.env,
            )
            sim.AnimateText(
                x=1078,
                y=y - 1,
                fontsize=10,
                textcolor=TEXT_FILL,
                text=label,
                env=self.env,
            )

    def _draw_footer(self) -> None:
        sim.AnimateText(
            x=44,
            y=22,
            fontsize=10,
            textcolor=TEXT_MUTED,
            text="La simulacion y la visualizacion comparten el mismo estado; el dashboard no altera la logica academica.",
            env=self.env,
        )

    def _metric_card(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        label: str,
        value: str,
        detail: str,
        accent: str,
    ) -> None:
        sim.AnimateRectangle(
            spec=(x, y - height, x + width, y),
            fillcolor=CARD_FILL,
            linecolor=accent,
            linewidth=1,
            env=self.env,
        )
        sim.AnimateText(
            x=x + 16,
            y=y - 15,
            fontsize=10,
            textcolor=TEXT_MUTED,
            text=label,
            env=self.env,
        )
        sim.AnimateText(
            x=x + 16,
            y=y - 34,
            fontsize=16,
            textcolor=TEXT_FILL,
            text=value,
            env=self.env,
        )
        if detail:
            sim.AnimateText(
                x=x + 245,
                y=y - 33,
                fontsize=9,
                textcolor=TEXT_MUTED,
                text=detail,
                env=self.env,
            )

    def _status_chip(self, x: float, y: float, label: str, value, color: str) -> None:
        sim.AnimateRectangle(
            spec=(x, y - 16, x + 296, y + 8),
            fillcolor=CARD_FILL,
            linecolor=color,
            linewidth=1,
            env=self.env,
        )
        sim.AnimateText(
            x=x + 14,
            y=y - 1,
            fontsize=10,
            textcolor=TEXT_MUTED,
            text=label,
            env=self.env,
        )
        sim.AnimateText(
            x=x + 118,
            y=y - 1,
            fontsize=10,
            textcolor=TEXT_FILL,
            text=(lambda _arg, _t, value=value: value() if callable(value) else value),
            env=self.env,
        )

    def _student_fill(self, student: StudentState) -> str:
        return TECH_ACCESS_FILL.get(student.technology_access, TECH_ACCESS_FILL["bajo"])

    def _student_border(self, student: StudentState) -> str:
        status = student.visual_status()
        if status == "approved":
            return STATUS_BORDER["approved"]
        if status == "deserted":
            return STATUS_BORDER["deserted"]
        return RISK_BORDER[student.visual_risk_level()]

    def _student_tile_text(self, student: StudentState) -> str:
        status = student.visual_status()

        if status == "deserted":
            title = "DESERTO"
        elif status == "approved":
            title = "APROBADO"
        else:
            title = f"R {RISK_LABELS[student.visual_risk_level()]}"

        line = f"{student.student_id:02d} | {student.current_grade:04.1f}"
        if self.show_ml_metrics and student.ml_risk_level != "bajo":
            return f"{line}\n{title}\nML {student.ml_risk_level}"

        return f"{line}\n{title}"

    def _snapshot(self) -> _KpiSnapshot:
        total = len(self.students)
        if total == 0:
            return _KpiSnapshot(0.0, 0.0, 0, 0, 0, 0)

        approved = sum(1 for student in self.students if student.approved)
        deserted = sum(1 for student in self.students if student.deserted)
        active = total - deserted

        return _KpiSnapshot(
            average_grade=mean(student.current_grade for student in self.students),
            average_risk=mean(student.desertion_risk for student in self.students),
            approved=approved,
            deserted=deserted,
            active=active,
            ml_high=sum(1 for student in self.students if student.ml_risk_level == "alto"),
        )

    def _progress_ratio(self) -> float:
        if self.semester_weeks <= 0:
            return 0.0

        return max(0.0, min(self.env.now() / self.semester_weeks, 1.0))

    @staticmethod
    def _risk_accent(value: float) -> str:
        if value < 0.33:
            return RISK_BORDER["bajo"]
        if value < 0.66:
            return RISK_BORDER["medio"]
        return RISK_BORDER["alto"]
