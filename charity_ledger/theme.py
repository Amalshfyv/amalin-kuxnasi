import flet as ft

PRIMARY = "#2196F3"
PRIMARY_DARK = "#1E88E5"
PRIMARY_LIGHT = "#E3F2FD"

BG_APP = "#F8F9FB"
BG_CARD = "#FFFFFF"
BG_SIDEBAR = "#FAFBFC"

BORDER = "#E5E7EB"
DIVIDER = "#EEF0F3"

TEXT_PRIMARY = "#0F172A"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94A3B8"
TEXT_PLACEHOLDER = "#A1A8B3"

SUCCESS = "#10B981"
SUCCESS_BG = "#ECFDF5"
WARNING = "#F59E0B"
WARNING_BG = "#FFFBEB"
DANGER = "#EF4444"
DANGER_BG = "#FEF2F2"

TIER_PLATINUM_BG = "#EEF0FF"
TIER_PLATINUM_FG = "#6B6BE3"
TIER_GOLD_BG = "#FEF3C7"
TIER_GOLD_FG = "#B45309"
TIER_SILVER_BG = "#F1F5F9"
TIER_SILVER_FG = "#475569"
TIER_BRONZE_BG = "#FEE7DA"
TIER_BRONZE_FG = "#9A3412"

CARD_RADIUS = 12
PILL_RADIUS = 999
INPUT_RADIUS = 8

SHADOW = ft.BoxShadow(
    spread_radius=0,
    blur_radius=12,
    color="#0F172A14",
    offset=ft.Offset(0, 2),
)

SHADOW_SOFT = ft.BoxShadow(
    spread_radius=0,
    blur_radius=6,
    color="#0F172A0D",
    offset=ft.Offset(0, 1),
)


def card(content, padding=20, expand=None, width=None, height=None, bgcolor=BG_CARD):
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=bgcolor,
        border=ft.border.all(1, BORDER),
        border_radius=CARD_RADIUS,
        expand=expand,
        width=width,
        height=height,
    )


def section_title(text, size=20, weight=ft.FontWeight.W_700):
    return ft.Text(text, size=size, weight=weight, color=TEXT_PRIMARY)


def subtitle(text, size=13):
    return ft.Text(text, size=size, color=TEXT_SECONDARY)


def muted(text, size=12):
    return ft.Text(text, size=size, color=TEXT_MUTED)


def primary_button(text, icon=None, on_click=None, expand=None, height=40):
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        expand=expand,
        height=height,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY,
            color="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation=0,
            padding=ft.padding.symmetric(horizontal=18, vertical=10),
            text_style=ft.TextStyle(weight=ft.FontWeight.W_600, size=13),
        ),
    )


def outline_button(text, icon=None, on_click=None, expand=None, height=40):
    return ft.OutlinedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        expand=expand,
        height=height,
        style=ft.ButtonStyle(
            color=TEXT_PRIMARY,
            side=ft.BorderSide(1, BORDER),
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            text_style=ft.TextStyle(weight=ft.FontWeight.W_600, size=13),
        ),
    )


def status_pill(label: str):
    label_l = (label or "").lower()
    if label_l in ("verified", "active", "operational"):
        bg, fg, icon = SUCCESS_BG, SUCCESS, ft.Icons.CHECK_CIRCLE_OUTLINE
    elif label_l in ("pending", "in progress"):
        bg, fg, icon = WARNING_BG, WARNING, ft.Icons.SCHEDULE
    elif label_l in ("failed", "on hold"):
        bg, fg, icon = DANGER_BG, DANGER, ft.Icons.ERROR_OUTLINE
    else:
        bg, fg, icon = TIER_SILVER_BG, TIER_SILVER_FG, ft.Icons.INFO_OUTLINE
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, size=12, color=fg),
                ft.Text(label, size=11, color=fg, weight=ft.FontWeight.W_600),
            ],
            spacing=4,
            tight=True,
        ),
        bgcolor=bg,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
        border_radius=PILL_RADIUS,
    )


def tier_pill(tier: str):
    t = (tier or "").lower()
    if t == "platinum":
        bg, fg = TIER_PLATINUM_BG, TIER_PLATINUM_FG
    elif t == "gold":
        bg, fg = TIER_GOLD_BG, TIER_GOLD_FG
    elif t == "bronze":
        bg, fg = TIER_BRONZE_BG, TIER_BRONZE_FG
    else:
        bg, fg = TIER_SILVER_BG, TIER_SILVER_FG
    return ft.Container(
        content=ft.Text(tier, size=11, color=fg, weight=ft.FontWeight.W_600),
        bgcolor=bg,
        padding=ft.padding.symmetric(horizontal=10, vertical=3),
        border_radius=PILL_RADIUS,
    )


def divider(h=1, color=DIVIDER):
    return ft.Container(height=h, bgcolor=color)


def fmt_money(v: float, decimals: int = 0) -> str:
    if decimals:
        return f"${v:,.{decimals}f}"
    return f"${v:,.0f}"


def fmt_money_k(v: float) -> str:
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"${int(v/1000)}k"
    return f"${v:.0f}"
