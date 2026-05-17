import flet as ft

from .. import db, theme as T
from ..components.cards import kpi_card, progress_row
from ..components.charts import line_chart


def _page_header(on_new_project, on_generate_report):
    return ft.Row(
        [
            ft.Column(
                [
                    T.section_title("Admin Dashboard", size=24),
                    T.subtitle("Welcome back, Amal. Here is what is happening with your projects today."),
                ],
                spacing=4,
                expand=True,
            ),
            T.outline_button("Generate Report", icon=ft.Icons.INSERT_CHART_OUTLINED, on_click=on_generate_report),
            ft.Container(width=8),
            T.primary_button("New Project", icon=ft.Icons.ADD, on_click=on_new_project),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _kpi_strip_equal():
    k = db.kpis()
    cards = [
        kpi_card("Total Funds Raised", T.fmt_money(k["total_funds"]),
                 ft.Icons.NORTH_EAST, delta="+12.5%", delta_positive=True),
        kpi_card("Active Projects", str(k["active"]),
                 ft.Icons.WORK_OUTLINE, delta="+2", delta_positive=True),
        kpi_card("Total Donors", f"{k['donors']:,}",
                 ft.Icons.PEOPLE_OUTLINE, delta="+48", delta_positive=True),
        kpi_card("Pending Verification", str(k["pending"]),
                 ft.Icons.SCHEDULE, delta="-14", delta_positive=False,
                 icon_bg="#FEF3C7", icon_fg=T.WARNING),
    ]
    return ft.Row(
        [ft.Container(c, expand=1) for c in cards],
        spacing=14,
    )


def _donation_trends_card(on_full_analysis):
    rows = db.donation_trends()
    labels = [r["month"] for r in rows]
    values = [r["amount"] for r in rows]
    return T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                T.section_title("Donation Trends", size=16),
                                T.subtitle("Monthly contribution volume over the last 6 months"),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.TextButton(
                            "Full Analysis",
                            on_click=on_full_analysis,
                            style=ft.ButtonStyle(color=T.PRIMARY, text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600)),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=10),
                ft.Container(content=line_chart(labels, values, height=240), height=240),
            ],
            spacing=0,
        ),
        padding=20,
        expand=True,
    )


def _project_funding_card(on_view_all):
    rows = db.list_projects()[:4]
    items = [progress_row(r["name"], r["raised"], r["goal"]) for r in rows]
    return T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                T.section_title("Project Funding", size=16),
                                T.subtitle("Real-time progress of top initiatives"),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.TextButton(
                            "View All",
                            on_click=lambda e: on_view_all(),
                            style=ft.ButtonStyle(color=T.PRIMARY, text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600)),
                        ),
                    ],
                ),
                ft.Container(height=10),
                ft.Column(
                    [items[0], ft.Container(height=10), items[1], ft.Container(height=10), items[2], ft.Container(height=10), items[3]] if len(items) >= 4 else items,
                    spacing=0,
                ),
            ],
            spacing=0,
        ),
        padding=20,
        width=380,
    )


def _recent_tx_card(on_audit, on_audit_ledger):
    txs = db.list_transactions(limit=5)
    headers = [
        ft.DataColumn(ft.Text("TX ID", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Donor", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Project", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Date", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Amount", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Status", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Actions", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
    ]
    rows = []
    for t in txs:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(t["id"], size=12, color=T.PRIMARY, weight=ft.FontWeight.W_600)),
                    ft.DataCell(ft.Text(t["donor"], size=12, color=T.TEXT_PRIMARY)),
                    ft.DataCell(ft.Text(t["project"], size=12, color=T.TEXT_SECONDARY)),
                    ft.DataCell(ft.Text(t["date"], size=12, color=T.TEXT_SECONDARY)),
                    ft.DataCell(ft.Text(T.fmt_money(t["amount"]), size=12, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_700)),
                    ft.DataCell(T.status_pill(t["status"])),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.OPEN_IN_NEW,
                        icon_size=14,
                        icon_color=T.PRIMARY,
                        tooltip="View audit details",
                        on_click=lambda e, tx=t: on_audit(tx["id"]),
                    )),
                ]
            )
        )
    table = ft.DataTable(
        columns=headers,
        rows=rows,
        heading_row_height=36,
        data_row_min_height=48,
        data_row_max_height=52,
        divider_thickness=0,
        column_spacing=24,
        horizontal_margin=4,
    )
    return T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                T.section_title("Recent Transactions", size=16),
                                T.subtitle("Latest financial movements across all verified ledgers"),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        T.outline_button("Audit Ledger", icon=ft.Icons.OPEN_IN_NEW, on_click=on_audit_ledger),
                    ],
                ),
                ft.Container(height=12),
                table,
            ],
            spacing=0,
        ),
        padding=20,
    )


def view(on_nav, on_new_project, on_view_all_projects, on_audit_tx,
         on_generate_report, on_audit_ledger, on_full_analysis):
    return ft.Column(
        [
            _page_header(on_new_project, on_generate_report),
            ft.Container(height=18),
            _kpi_strip_equal(),
            ft.Container(height=18),
            ft.Row(
                [
                    _donation_trends_card(on_full_analysis),
                    _project_funding_card(on_view_all_projects),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(height=18),
            _recent_tx_card(on_audit_tx, on_audit_ledger),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
    )
