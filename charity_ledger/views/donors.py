import flet as ft

from .. import db, theme as T
from ..components.cards import avatar_initials, kpi_card
from ..components.charts import bar_chart


TIER_OPTIONS = ["All", "Platinum", "Gold", "Silver", "Bronze"]


def _donor_row(d, on_select, selected_id, on_action):
    is_sel = d["id"] == selected_id
    more_menu = ft.PopupMenuButton(
        icon=ft.Icons.MORE_HORIZ,
        items=[
            ft.PopupMenuItem(text="View Full Profile", icon=ft.Icons.PERSON, on_click=lambda e: on_action(d["id"], "profile")),
            ft.PopupMenuItem(text="Send Message", icon=ft.Icons.MAIL_OUTLINE, on_click=lambda e: on_action(d["id"], "message")),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="Tier Status", icon=ft.Icons.STAR_OUTLINE, on_click=lambda e: on_action(d["id"], "tier")),
        ],
    )
    return ft.Container(
        on_click=lambda e: on_select(d["id"]),
        ink=True,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        bgcolor=T.PRIMARY_LIGHT if is_sel else None,
        border_radius=8,
        content=ft.Row(
            [
                avatar_initials(d["name"], size=32),
                ft.Container(width=4),
                ft.Text(d["name"], size=13, weight=ft.FontWeight.W_700 if is_sel else ft.FontWeight.W_600, color=T.TEXT_PRIMARY, expand=2),
                ft.Container(content=T.tier_pill(d["tier"] or "Silver"), expand=1),
                ft.Text(T.fmt_money(d["total_donated"]), size=13, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY, expand=1),
                ft.Text(d["last_activity"], size=12, color=T.TEXT_MUTED, expand=1),
                more_menu,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
    )


def _directory_card(donors, selected_id, on_select, tier_filter, on_tier_filter, on_action):
    header = ft.Row(
        [
            ft.Text("Donor", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Tier", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600, expand=1),
            ft.Text("Total Donated", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600, expand=1),
            ft.Text("Last Activity", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600, expand=1),
            ft.Container(width=44),
        ],
        spacing=10,
    )
    if tier_filter and tier_filter != "All":
        donors = [d for d in donors if d["tier"] == tier_filter]
    rows = [_donor_row(d, on_select, selected_id, on_action) for d in donors] or [
        ft.Container(padding=ft.padding.all(20),
                     content=ft.Text("No donors match the current filter.", color=T.TEXT_MUTED, size=12),
                     alignment=ft.alignment.center),
    ]
    tier_dd = ft.Dropdown(
        value=tier_filter or "All",
        options=[ft.dropdown.Option(t) for t in TIER_OPTIONS],
        border_color=T.BORDER, border_radius=8, text_size=12,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        width=140,
        on_change=lambda e: on_tier_filter(e.control.value),
    )
    return T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                T.section_title("Donor Directory", size=16),
                                T.subtitle("A complete list of active contributors and their lifetime impact."),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        tier_dd,
                    ]
                ),
                ft.Container(height=12),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    bgcolor=T.BG_CARD,
                    content=header,
                ),
                T.divider(),
                ft.Container(height=4),
                ft.Column(rows, spacing=6),
            ],
            spacing=0,
        ),
        padding=20,
        expand=True,
    )


def _profile_card(d, on_full_profile, on_phone):
    if not d:
        return T.card(ft.Text("No donor selected", color=T.TEXT_MUTED), expand=True)
    return T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(expand=True),
                        avatar_initials(d["name"], size=84, bg=T.PRIMARY_LIGHT, fg=T.PRIMARY),
                        ft.Container(expand=True),
                    ],
                ),
                ft.Container(height=12),
                ft.Row(
                    [
                        ft.Text(d["name"], size=18, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                        ft.Container(expand=True),
                        T.tier_pill(d["tier"] or "Silver"),
                    ]
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.MAIL_OUTLINE, size=14, color=T.TEXT_MUTED),
                        ft.Text(d["email"] or "", size=12, color=T.TEXT_SECONDARY),
                    ],
                    spacing=6,
                ),
                ft.Container(height=14),
                T.divider(),
                ft.Container(height=14),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("LOCATION", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                                ft.Container(height=2),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color=T.PRIMARY),
                                        ft.Text(d["location"] or "—", size=12, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            expand=True,
                            spacing=0,
                        ),
                        ft.Column(
                            [
                                ft.Text("JOINED", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                                ft.Container(height=2),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=12, color=T.PRIMARY),
                                        ft.Text(d["joined"] or "—", size=12, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            expand=True,
                            spacing=0,
                        ),
                    ],
                ),
                ft.Container(height=14),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("PROJECTS SUPPORTED", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                                ft.Container(height=2),
                                ft.Text(f"{d['projects_supported'] or 0} Active", size=12, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                            ],
                            expand=True,
                            spacing=0,
                        ),
                        ft.Column(
                            [
                                ft.Text("PHONE", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                                ft.Container(height=2),
                                ft.Text(d["phone"] or "—", size=12, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                            ],
                            expand=True,
                            spacing=0,
                        ),
                    ],
                ),
                ft.Container(height=18),
                ft.Row(
                    [
                        T.primary_button("Full Profile View", on_click=lambda e: on_full_profile(d["id"]), expand=True),
                        ft.Container(width=8),
                        ft.IconButton(
                            icon=ft.Icons.PHONE,
                            icon_color=T.TEXT_PRIMARY,
                            tooltip="Copy phone number",
                            bgcolor=T.BG_CARD,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, T.BORDER),
                            ),
                            on_click=lambda e: on_phone(d["id"]),
                        ),
                    ]
                ),
            ],
            spacing=4,
        ),
        padding=22,
    )


def _donation_trend_card():
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    values = [40, 38, 45, 60, 95, 80]
    return T.card(
        ft.Column(
            [
                ft.Text("DONATION TREND (LAST 6 MO)", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                ft.Container(height=10),
                ft.Container(content=bar_chart(labels, values, height=160), height=180),
            ],
            spacing=0,
        ),
        padding=20,
    )


def _top_projects_card():
    items = [
        ("Clean Water Initiative", "Charity #0420", 4500, T.PRIMARY),
        ("Urban Tech Scholarships", "Charity #0421", 2800, T.SUCCESS),
        ("Global Forest Recovery", "Charity #0422", 1200, T.SUCCESS),
    ]
    rows = []
    for name, sub, amt, color in items:
        rows.append(
            ft.Row(
                [
                    ft.Container(width=3, height=32, bgcolor=color, border_radius=2),
                    ft.Container(width=8),
                    ft.Column(
                        [
                            ft.Text(name, size=12, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                            ft.Text(sub, size=11, color=T.TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Text(T.fmt_money(amt), size=13, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                ]
            )
        )
    return T.card(
        ft.Column(
            [
                ft.Text("TOP SUPPORTED PROJECTS", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                ft.Container(height=10),
                ft.Column(
                    [r for pair in zip(rows, [ft.Container(height=10)] * len(rows)) for r in pair][:-1],
                    spacing=0,
                ),
            ],
            spacing=0,
        ),
        padding=20,
    )


def _kpi_strip():
    cards = [
        kpi_card("RETENTION RATE", "84.2%", ft.Icons.SHIELD_OUTLINED, delta="+2.1%", delta_positive=True),
        kpi_card("AVG. GIFT SIZE", "$480", ft.Icons.NORTH_EAST, delta="+12%", delta_positive=True),
        kpi_card("NEW DONORS", "128", ft.Icons.FAVORITE_BORDER, delta=None),
    ]
    return ft.Row(
        [
            ft.Container(cards[0], expand=1),
            ft.Container(cards[1], expand=1),
            ft.Container(cards[2], expand=1),
        ],
        spacing=14,
    )


def view(on_select, selected_id, tier_filter, on_tier_filter,
         on_export, on_broadcast, on_donor_action, on_full_profile, on_phone):
    donors = db.list_donors()
    if selected_id is None and donors:
        selected_id = donors[0]["id"]
    selected = next((d for d in donors if d["id"] == selected_id), donors[0] if donors else None)

    left = ft.Column(
        [
            _directory_card(donors, selected["id"] if selected else None, on_select,
                            tier_filter, on_tier_filter, on_donor_action),
            ft.Container(height=18),
            _kpi_strip(),
        ],
        spacing=0,
    )
    right = ft.Column(
        [
            _profile_card(selected, on_full_profile, on_phone),
            ft.Container(height=18),
            _donation_trend_card(),
            ft.Container(height=18),
            _top_projects_card(),
        ],
        width=360,
        spacing=0,
    )
    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            T.section_title("Donors Management", size=24),
                            T.subtitle("Manage, analyze, and engage with your donor community."),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    T.outline_button("Export CSV", icon=ft.Icons.FILE_DOWNLOAD_OUTLINED, on_click=on_export),
                    ft.Container(width=8),
                    T.primary_button("Broadcast Message", icon=ft.Icons.MAIL_OUTLINE, on_click=on_broadcast),
                ],
            ),
            ft.Container(height=18),
            ft.Row(
                [
                    ft.Container(left, expand=True),
                    ft.Container(width=18),
                    right,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
