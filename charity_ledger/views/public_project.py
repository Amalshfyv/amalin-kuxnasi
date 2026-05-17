import flet as ft

from .. import db, theme as T
from ..components.shell import brand
from ..components.cards import avatar_initials


def _public_topbar(on_admin_login):
    return ft.Container(
        height=64,
        padding=ft.padding.symmetric(horizontal=24, vertical=10),
        bgcolor=ft.colors.ON_PRIMARY,
        border=ft.border.only(bottom=ft.BorderSide(1, T.BORDER)),
        content=ft.Row(
            [
                brand(size=18),
                ft.Container(expand=True),
                ft.Stack(
                    [
                        ft.Icon(ft.Icons.NOTIFICATIONS_NONE, color=T.TEXT_SECONDARY, size=22),
                        ft.Container(width=8, height=8, bgcolor=T.DANGER, border_radius=999, top=0, right=0),
                    ],
                    width=24,
                    height=24,
                ),
                ft.Container(width=12),
                T.outline_button("Admin Login", on_click=on_admin_login),
            ]
        ),
    )


def _hero(project, on_donate, on_learn_more):
    return ft.Container(
        height=320,
        padding=ft.padding.all(40),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[ft.colors.PRIMARY_CONTAINER, ft.colors.PRIMARY],
        ),
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.colors.ON_PRIMARY, size=14),
                            ft.Text("Verified Humanitarian Project", size=12, color=ft.colors.ON_PRIMARY, weight=ft.FontWeight.W_700),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    bgcolor="#10B981",
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=999,
                ),
                ft.Container(height=18),
                ft.Text(
                    "Clean Water for West\nAfrican Schools",
                    size=44,
                    weight=ft.FontWeight.W_800,
                    color=ft.colors.ON_PRIMARY,
                ),
                ft.Container(height=10),
                ft.Text(
                    "Providing sustainable filtration systems and well infrastructure to 15\nrural schools, impacting over 4,500 students.",
                    size=14,
                    color="#E0F2FE",
                ),
                ft.Container(height=22),
                ft.Row(
                    [
                        T.primary_button("Donate Now", icon=ft.Icons.ARROW_FORWARD,
                                         on_click=lambda e: on_donate()),
                        ft.Container(width=10),
                        ft.OutlinedButton(
                            text="Learn More",
                            on_click=lambda e: on_learn_more(),
                            style=ft.ButtonStyle(
                                color=ft.colors.ON_PRIMARY,
                                side=ft.BorderSide(1, T.BG_CARD),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=18, vertical=10),
                                text_style=ft.TextStyle(weight=ft.FontWeight.W_600, size=13),
                            ),
                        ),
                    ]
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )


def _progress_strip(project, on_donate):
    raised = project["raised"] if project else 36000
    goal = project["goal"] if project else 50000
    pct = int(raised / goal * 100) if goal else 0
    return T.card(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(T.fmt_money(raised), size=24, weight=ft.FontWeight.W_700),
                                ft.Container(width=10),
                                ft.Text(f"of {T.fmt_money(goal)}", size=13, color=T.TEXT_MUTED),
                                ft.Container(expand=True),
                                ft.Text(f"{pct}%", size=14, weight=ft.FontWeight.W_700, color=T.PRIMARY),
                            ]
                        ),
                        ft.ProgressBar(
                            value=pct / 100,
                            color=T.PRIMARY,
                            bgcolor="#E5EEF6",
                            bar_height=6,
                            border_radius=999,
                        ),
                        ft.Container(height=8),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=12, color=T.TEXT_MUTED),
                                ft.Text("412 Backers", size=11, color=T.TEXT_SECONDARY),
                                ft.Container(width=18),
                                ft.Icon(ft.Icons.TRENDING_UP, size=12, color=T.TEXT_MUTED),
                                ft.Text("12 Days Remaining", size=11, color=T.TEXT_SECONDARY),
                                ft.Container(width=18),
                                ft.Icon(ft.Icons.SHIELD_OUTLINED, size=12, color=T.TEXT_MUTED),
                                ft.Text("Fully Audited", size=11, color=T.TEXT_SECONDARY),
                            ],
                            spacing=4,
                        ),
                    ],
                    expand=True,
                    spacing=4,
                ),
                ft.Container(width=24),
                ft.Column(
                    [
                        T.primary_button("Contribute Now", on_click=lambda e: on_donate(), height=44),
                        ft.Container(height=4),
                        ft.Text("100% GOES DIRECTLY TO PROJECT", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
    )


def _challenge_section():
    return ft.Column(
        [
            T.section_title("The Challenge & Our Mission", size=22),
            ft.Container(height=10),
            ft.Text(
                "In many rural communities across the West African coast, children spend up to 4 hours a day walking to fetch water. Not only does this keep them away from school, but the water sources are often contaminated, leading to preventable diseases that hinder community growth.",
                size=13,
                color=T.TEXT_SECONDARY,
            ),
            ft.Container(height=10),
            ft.Text(
                "Our mission is to install deep-bore solar-powered wells and ultra-filtration systems directly on school grounds.",
                size=13,
                color=T.TEXT_PRIMARY,
                weight=ft.FontWeight.W_700,
            ),
            ft.Container(height=10),
            ft.Text(
                "By providing immediate access to clean water, we aren't just improving health; we are increasing school attendance rates by an estimated 35% and empowering a new generation of students to focus on their education rather than survival.",
                size=13,
                color=T.TEXT_SECONDARY,
            ),
            ft.Container(height=14),
            ft.Row(
                [
                    ft.Container(width=140, height=110, border_radius=10, bgcolor="#1976D2",
                                 content=ft.Icon(ft.Icons.WATER_DROP, size=36, color=ft.colors.ON_PRIMARY),
                                 alignment=ft.alignment.center),
                    ft.Container(width=140, height=110, border_radius=10, bgcolor="#0EA5E9",
                                 content=ft.Icon(ft.Icons.SOLAR_POWER, size=36, color=ft.colors.ON_PRIMARY),
                                 alignment=ft.alignment.center),
                    ft.Container(width=140, height=110, border_radius=10, bgcolor="#B45309",
                                 content=ft.Icon(ft.Icons.LANDSCAPE, size=36, color=ft.colors.ON_PRIMARY),
                                 alignment=ft.alignment.center),
                ],
                spacing=10,
            ),
        ],
        spacing=0,
    )


def _impact_tier(amount, desc, icon, on_donate):
    return T.card(
        ft.Container(
            on_click=lambda e: on_donate(),
            ink=True,
            padding=ft.padding.all(12),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=18, color=T.PRIMARY),
                        width=36, height=36,
                        bgcolor=T.PRIMARY_LIGHT,
                        border_radius=999,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(height=10),
                    ft.Text(amount, size=22, weight=ft.FontWeight.W_700, color=T.PRIMARY),
                    ft.Container(height=4),
                    ft.Text(desc, size=12, color=T.TEXT_SECONDARY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
        ),
        padding=6,
        bgcolor=T.PRIMARY_LIGHT,
    )


def _impact_tiers_card(on_donate):
    return T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=T.PRIMARY),
                        T.section_title("Impact Tiers", size=15),
                    ],
                    spacing=6,
                ),
                ft.Container(height=10),
                _impact_tier("$50", "Provides a personal bio-sand filter for 1 student's family.", ft.Icons.WATER_DROP_OUTLINED, on_donate),
                ft.Container(height=10),
                _impact_tier("$250", "Funds the annual maintenance for one solar pump.", ft.Icons.CHECK_CIRCLE_OUTLINE, on_donate),
                ft.Container(height=10),
                _impact_tier("$1,000", "Installs a 5,000L water storage tank for a school.", ft.Icons.SHIELD_OUTLINED, on_donate),
            ],
            spacing=0,
        ),
        padding=20,
        width=300,
    )


def _ledger_table(on_view_history):
    txs = db.list_transactions(limit=5)
    headers = [
        ft.DataColumn(ft.Text("Transaction ID", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Donor", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Amount", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Time", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Verification", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
    ]
    rows = []
    for t in txs:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(t["id"].lower(), size=12, color=T.TEXT_SECONDARY)),
                    ft.DataCell(
                        ft.Row(
                            [avatar_initials(t["donor"], size=24), ft.Text(t["donor"], size=12, color=T.TEXT_PRIMARY)],
                            spacing=8,
                        )
                    ),
                    ft.DataCell(ft.Text(T.fmt_money(t["amount"]), size=12, weight=ft.FontWeight.W_700)),
                    ft.DataCell(ft.Text(t["date"], size=12, color=T.TEXT_SECONDARY)),
                    ft.DataCell(T.status_pill(t["status"])),
                ]
            )
        )
    table = ft.DataTable(
        columns=headers,
        rows=rows,
        heading_row_height=36,
        data_row_min_height=44,
        data_row_max_height=48,
        column_spacing=24,
        divider_thickness=0,
        horizontal_margin=4,
    )
    return T.card(
        ft.Column(
            [
                ft.Container(
                    padding=ft.padding.all(14),
                    bgcolor=T.BG_APP,
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.HISTORY, size=14, color=T.PRIMARY),
                            ft.Text("Recent Verified Donations", size=13, weight=ft.FontWeight.W_700),
                        ],
                        spacing=6,
                    ),
                ),
                T.divider(),
                ft.Container(content=ft.Row([table], scroll=ft.ScrollMode.AUTO), padding=ft.padding.all(8)),
                T.divider(),
                ft.Container(
                    padding=ft.padding.all(14),
                    on_click=lambda e: on_view_history(),
                    ink=True,
                    content=ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.Text("View Full Transaction History", size=12, color=T.PRIMARY, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True),
                        ]
                    ),
                ),
            ],
            spacing=0,
        ),
        padding=0,
    )


def _ledger_section(on_download_audit, on_view_history):
    return ft.Column(
        [
            T.section_title("Transparency Ledger", size=22),
            ft.Container(height=8),
            ft.Row(
                [
                    ft.Text(
                        "Every donation to this project is tracked on our public ledger. We utilize cryptographic\nverification to ensure funds are allocated exactly where they were intended.",
                        size=13,
                        color=T.TEXT_SECONDARY,
                        expand=True,
                    ),
                    T.outline_button("Download Audit Report", icon=ft.Icons.OPEN_IN_NEW,
                                     on_click=lambda e: on_download_audit()),
                ],
            ),
            ft.Container(height=14),
            _ledger_table(on_view_history),
        ],
        spacing=0,
    )


def _public_footer(on_admin):
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=40, vertical=30),
        bgcolor=ft.colors.ON_PRIMARY,
        border=ft.border.only(top=ft.BorderSide(1, T.BORDER)),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                brand(size=15),
                                ft.Container(height=8),
                                ft.Text(
                                    "Empowering global trust through financial\ntransparency and real-time donation tracking.",
                                    size=12,
                                    color=T.TEXT_SECONDARY,
                                ),
                            ],
                            expand=True,
                            spacing=0,
                        ),
                        ft.Column(
                            [
                                ft.Text("TRANSPARENCY", size=11, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                                ft.Container(height=6),
                                ft.Text("Verified Ledger", size=12, color=T.TEXT_SECONDARY),
                                ft.Text("Audit Reports", size=12, color=T.TEXT_SECONDARY),
                                ft.Text("Beneficiary Verification", size=12, color=T.TEXT_SECONDARY),
                            ],
                            expand=True, spacing=4,
                        ),
                        ft.Column(
                            [
                                ft.Text("RESOURCES", size=11, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                                ft.Container(height=6),
                                ft.Text("How It Works", size=12, color=T.TEXT_SECONDARY),
                                ft.Text("Partner Charities", size=12, color=T.TEXT_SECONDARY),
                                ft.Text("Contact Support", size=12, color=T.TEXT_SECONDARY),
                            ],
                            expand=True, spacing=4,
                        ),
                        ft.Column(
                            [
                                ft.Text("CONTACT", size=11, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                                ft.Container(height=6),
                                ft.Text("info@charityledger.org", size=12, color=T.TEXT_SECONDARY),
                                ft.Text("+1 (555) 000-TRANSPARENCY", size=12, color=T.TEXT_SECONDARY),
                            ],
                            expand=True, spacing=4,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=18),
                T.divider(),
                ft.Container(height=12),
                ft.Row(
                    [
                        ft.Text("© 2024 Charity Transparency Ledger. All rights reserved.", size=11, color=T.TEXT_MUTED),
                        ft.Container(expand=True),
                        ft.Text("Twitter", size=11, color=T.TEXT_MUTED),
                        ft.Container(width=14),
                        ft.Text("LinkedIn", size=11, color=T.TEXT_MUTED),
                        ft.Container(width=14),
                        ft.TextButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.SHIELD_OUTLINED, size=12, color=T.PRIMARY),
                                    ft.Text("Admin Dashboard", size=11, weight=ft.FontWeight.W_600),
                                ],
                                spacing=4,
                                tight=True,
                            ),
                            style=ft.ButtonStyle(color=T.PRIMARY),
                            on_click=lambda e: on_admin(),
                        ),
                    ]
                ),
            ],
            spacing=0,
        ),
    )


def view(project_id, on_donate, on_admin_login, on_download_audit, on_view_history, on_learn_more):
    project = db.get_project(project_id) if project_id else None
    return ft.Column(
        [
            _public_topbar(on_admin_login),
            ft.Container(
                content=ft.Column(
                    [
                        _hero(project, on_donate, on_learn_more),
                        ft.Container(
                            content=ft.Container(
                                content=_progress_strip(project, on_donate),
                                margin=ft.margin.only(top=-40, left=40, right=40),
                            ),
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=40, vertical=30),
                            content=ft.Row(
                                [
                                    ft.Container(_challenge_section(), expand=2),
                                    ft.Container(width=24),
                                    _impact_tiers_card(on_donate),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=40, vertical=10),
                            content=T.divider(),
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=40, vertical=30),
                            content=_ledger_section(on_download_audit, on_view_history),
                        ),
                        _public_footer(on_admin_login),
                    ],
                    spacing=0,
                ),
                bgcolor=T.BG_APP,
            ),
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
