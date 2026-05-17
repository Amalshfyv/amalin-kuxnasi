import flet as ft
from .. import theme as T


NAV_ITEMS = [
    ("dashboard", "Dashboard", ft.Icons.GRID_VIEW_ROUNDED),
    ("projects", "Projects", ft.Icons.FOLDER_OPEN_OUTLINED),
    ("donors", "Donors", ft.Icons.PEOPLE_ALT_OUTLINED),
    ("beneficiaries", "Beneficiaries", ft.Icons.VOLUNTEER_ACTIVISM_OUTLINED),
    ("transactions", "Transactions", ft.Icons.SWAP_HORIZ_ROUNDED),
    ("reports", "Reports", ft.Icons.INSERT_CHART_OUTLINED_ROUNDED),
]


def brand(size=18):
    return ft.Row(
        [
            ft.Container(
                content=ft.Icon(ft.Icons.SHIELD_OUTLINED, color=ft.colors.ON_PRIMARY, size=14),
                width=26,
                height=26,
                bgcolor=T.PRIMARY,
                border_radius=6,
                alignment=ft.alignment.center,
            ),
            ft.Text(
                "Charity Transparency Ledger",
                size=size,
                weight=ft.FontWeight.W_700,
                color=T.PRIMARY,
            ),
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    )


def _nav_button(key, label, icon, active, on_click):
    bg = T.PRIMARY_LIGHT if active else None
    fg = T.PRIMARY if active else T.TEXT_SECONDARY
    weight = ft.FontWeight.W_600 if active else ft.FontWeight.W_500
    return ft.Container(
        key=f"nav-{key}",
        content=ft.Row(
            [
                ft.Icon(icon, color=fg, size=18),
                ft.Text(label, color=fg, size=13, weight=weight),
            ],
            spacing=10,
            tight=True,
        ),
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        margin=ft.margin.symmetric(horizontal=8, vertical=2),
        bgcolor=bg,
        border_radius=8,
        on_click=lambda e: on_click(key) if on_click else None,
        ink=True,
    )


def sidebar(active_key, on_nav, on_public_view=None, on_logout=None, on_settings=None):
    items = [_nav_button(k, l, i, k == active_key, on_nav) for k, l, i in NAV_ITEMS]
    return ft.Container(
        width=240,
        bgcolor=T.BG_SIDEBAR,
        border=ft.border.only(right=ft.BorderSide(1, T.BORDER)),
        content=ft.Column(
            [
                ft.Container(
                    content=brand(size=15),
                    padding=ft.padding.symmetric(horizontal=16, vertical=20),
                ),
                ft.Container(
                    content=ft.Text(
                        "MAIN MENU",
                        size=10,
                        color=T.TEXT_MUTED,
                        weight=ft.FontWeight.W_700,
                    ),
                    padding=ft.padding.only(left=20, top=4, bottom=8),
                ),
                *items,
                ft.Container(expand=True),
                T.divider(),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.PUBLIC, color=T.TEXT_SECONDARY, size=18),
                            ft.Text("Public View", color=T.TEXT_SECONDARY, size=13),
                            ft.Container(expand=True),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=T.TEXT_MUTED, size=16),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    on_click=lambda e: on_public_view() if on_public_view else None,
                    ink=True,
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=T.TEXT_SECONDARY, size=18),
                            ft.Text("Settings", color=T.TEXT_SECONDARY, size=13),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    on_click=lambda e: on_settings() if on_settings else None,
                    ink=True,
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.LOGOUT, color=T.DANGER, size=18),
                            ft.Text("Logout", color=T.DANGER, size=13, weight=ft.FontWeight.W_600),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    on_click=lambda e: on_logout() if on_logout else None,
                    ink=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
    )


def topbar(user_name="Amal Admin", role="Administrator",
           on_search_change=None, on_search_value="", on_bell_click=None, notif_count=0):
    search_field = ft.TextField(
        value=on_search_value or "",
        hint_text="Search projects, donors, or tx IDs...",
        prefix_icon=ft.Icons.SEARCH,
        border=ft.InputBorder.OUTLINE,
        border_color=T.BORDER,
        border_radius=8,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=10),
        height=40,
        width=320,
        on_submit=lambda e: on_search_change(e.control.value) if on_search_change else None,
    )

    bell_inner = ft.Stack(
        [
            ft.Icon(ft.Icons.NOTIFICATIONS_NONE, color=T.TEXT_SECONDARY, size=22),
        ] + ([ft.Container(width=8, height=8, bgcolor=T.DANGER, border_radius=999, top=0, right=0)] if notif_count else []),
        width=24,
        height=24,
    )
    bell = ft.Container(
        content=bell_inner,
        padding=ft.padding.all(4),
        on_click=lambda e: on_bell_click() if on_bell_click else None,
        ink=True,
        border_radius=999,
        tooltip=f"{notif_count} notification(s)" if notif_count else "No notifications",
    )

    avatar = ft.CircleAvatar(
        content=ft.Text(user_name[0], size=12, weight=ft.FontWeight.W_700),
        radius=16,
        bgcolor=T.PRIMARY_LIGHT,
        color=T.PRIMARY,
    )
    return ft.Container(
        height=64,
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
        bgcolor=ft.colors.ON_PRIMARY,
        border=ft.border.only(bottom=ft.BorderSide(1, T.BORDER)),
        content=ft.Row(
            [
                search_field,
                ft.Container(expand=True),
                bell,
                ft.Container(width=8),
                ft.VerticalDivider(width=1, color=T.BORDER),
                ft.Column(
                    [
                        ft.Text(user_name, size=13, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                        ft.Text(role, size=11, color=T.TEXT_MUTED),
                    ],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                ),
                avatar,
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def footer():
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        border=ft.border.only(top=ft.BorderSide(1, T.BORDER)),
        bgcolor=ft.colors.ON_PRIMARY,
        content=ft.Row(
            [
                ft.Text(
                    "© 2024 Charity Transparency Ledger.  System Status: Operational",
                    size=11,
                    color=T.TEXT_MUTED,
                ),
                ft.Container(expand=True),
                ft.Text("Privacy Policy", size=11, color=T.TEXT_MUTED),
                ft.Container(width=14),
                ft.Text("Audit Log", size=11, color=T.TEXT_MUTED),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def shell(active_key, body, on_nav, on_public_view=None, on_logout=None, on_settings=None,
          on_search_change=None, on_search_value="", on_bell_click=None, notif_count=0):
    return ft.Row(
        [
            sidebar(active_key, on_nav, on_public_view=on_public_view, on_logout=on_logout, on_settings=on_settings),
            ft.Column(
                [
                    topbar(
                        on_search_change=on_search_change,
                        on_search_value=on_search_value,
                        on_bell_click=on_bell_click,
                        notif_count=notif_count,
                    ),
                    ft.Container(
                        content=body,
                        padding=ft.padding.symmetric(horizontal=28, vertical=22),
                        bgcolor=T.BG_APP,
                        expand=True,
                    ),
                    footer(),
                ],
                spacing=0,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )
