import flet as ft
from .. import theme as T


def kpi_card(label, value, icon, delta=None, delta_positive=True, icon_bg=None, icon_fg=None):
    delta_color = T.SUCCESS if delta_positive else T.DANGER
    delta_icon = ft.Icons.TRENDING_UP if delta_positive else ft.Icons.TRENDING_DOWN
    icon_widget = ft.Container(
        content=ft.Icon(icon, size=16, color=icon_fg or T.PRIMARY),
        width=32,
        height=32,
        bgcolor=icon_bg or T.PRIMARY_LIGHT,
        border_radius=8,
        alignment=ft.alignment.center,
    )
    delta_row = ft.Row(
        [
            ft.Icon(delta_icon, color=delta_color, size=14),
            ft.Text(delta, size=12, weight=ft.FontWeight.W_700, color=delta_color),
        ],
        spacing=4,
        tight=True,
    ) if delta else ft.Container(height=14)

    return T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(label, size=12, color=T.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                        ft.Container(expand=True),
                        icon_widget,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=4),
                ft.Text(value, size=24, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                ft.Container(height=4),
                delta_row,
            ],
            spacing=2,
        ),
        padding=18,
    )


def progress_row(title, raised, goal, pct=None):
    pct = pct if pct is not None else (raised / goal * 100 if goal else 0)
    sub = f"{T.fmt_money(raised)} of {T.fmt_money(goal)} goal"
    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(title, size=13, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                            ft.Text(sub, size=11, color=T.TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Text(f"{pct:.0f}%", size=13, weight=ft.FontWeight.W_700, color=T.PRIMARY),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=6),
            ft.ProgressBar(
                value=min(pct / 100, 1.0),
                color=T.PRIMARY,
                    bgcolor=T.BG_CARD,
                bar_height=6,
                border_radius=999,
            ),
        ],
        spacing=0,
    )


def avatar_initials(text, size=28, bg=None, fg=None):
    if bg is None:
        bg = T.PRIMARY_LIGHT
    if fg is None:
        fg = T.PRIMARY
    initials = "".join([w[0] for w in text.split()[:2]]).upper() if text else "?"
    return ft.CircleAvatar(
        content=ft.Text(initials, size=11, weight=ft.FontWeight.W_700),
        radius=size / 2,
        bgcolor=bg,
        color=fg,
    )
