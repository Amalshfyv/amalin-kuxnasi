import flet as ft
from .. import theme as T


def line_chart(labels, values, height=240, color=T.PRIMARY, fill=True):
    max_v = max(values) if values else 1
    if max_v <= 0:
        max_v = 1
    points = [ft.LineChartDataPoint(i, v) for i, v in enumerate(values)]
    line = ft.LineChartData(
        data_points=points,
        stroke_width=3,
        color=color,
        curved=True,
        stroke_cap_round=True,
        below_line_gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#80BBDEFB", "#00FFFFFF"],
        ) if fill else None,
    )

    step = max_v / 4 if max_v else 1

    def _y_label(v):
        return T.fmt_money_k(v)

    return ft.LineChart(
        data_series=[line],
        border=ft.border.all(0, "transparent"),
        horizontal_grid_lines=ft.ChartGridLines(interval=step, color=T.DIVIDER, width=1, dash_pattern=[3, 3]),
        vertical_grid_lines=None,
        left_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=i * step,
                    label=ft.Text(_y_label(i * step), size=10, color=T.TEXT_MUTED),
                )
                for i in range(5)
            ],
            labels_size=44,
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=i, label=ft.Text(lab, size=10, color=T.TEXT_MUTED))
                for i, lab in enumerate(labels)
            ],
            labels_size=24,
        ),
        tooltip_bgcolor="#0F172AEE",
        min_y=0,
        max_y=max_v * 1.05,
        min_x=0,
        max_x=len(labels) - 1 if labels else 1,
        expand=True,
        height=height,
    )


def bar_chart(labels, values, height=180, color=T.PRIMARY):
    max_v = max(values) if values else 1
    if max_v <= 0:
        max_v = 1
    bars = []
    for i, v in enumerate(values):
        bars.append(
            ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=v,
                        width=18,
                        color=color,
                        border_radius=4,
                    )
                ],
            )
        )
    return ft.BarChart(
        bar_groups=bars,
        border=ft.border.all(0, "transparent"),
        horizontal_grid_lines=ft.ChartGridLines(
            interval=max_v / 4 if max_v else 1,
            color=T.DIVIDER,
            width=1,
            dash_pattern=[3, 3],
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=i, label=ft.Text(lab, size=10, color=T.TEXT_MUTED))
                for i, lab in enumerate(labels)
            ],
            labels_size=22,
        ),
        left_axis=ft.ChartAxis(labels_size=0),
        max_y=max_v * 1.15,
        min_y=0,
        height=height,
        expand=True,
    )
