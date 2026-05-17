import flet as ft

from .. import db, theme as T
from ..components.cards import kpi_card, progress_row
from ..components.charts import line_chart, bar_chart


def _stat_card(title, subtitle, body):
    return T.card(
        ft.Column(
            [
                T.section_title(title, size=16),
                T.subtitle(subtitle),
                ft.Container(height=12),
                body,
            ],
            spacing=0,
        ),
        padding=20,
        expand=True,
    )


def _export_action(label, sub, icon, on_click):
    return ft.Container(
        on_click=on_click,
        ink=True,
        padding=ft.padding.all(14),
        border=ft.border.all(1, T.BORDER),
        border_radius=10,
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, size=18, color=T.PRIMARY),
                    width=36, height=36,
                    bgcolor=T.PRIMARY_LIGHT,
                    border_radius=8,
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    [
                        ft.Text(label, size=13, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                        ft.Text(sub, size=11, color=T.TEXT_MUTED),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Icon(ft.Icons.FILE_DOWNLOAD_OUTLINED, size=18, color=T.PRIMARY),
            ],
            spacing=10,
        ),
    )


def view(on_export_dashboard, on_export_donors, on_export_transactions,
         on_export_projects, on_export_beneficiaries, on_export_audit):
    trend = db.donation_trends()
    trend_labels = [r["month"] for r in trend]
    trend_values = [r["amount"] for r in trend]
    by_status = db.stats_by_status()
    status_keys = ["Verified", "Pending", "Failed"]
    status_values = [by_status.get(s, {"count": 0})["count"] for s in status_keys]
    by_cat = db.stats_by_category()
    cat_labels = [c["category"] or "—" for c in by_cat]
    cat_values = [c["total"] for c in by_cat]
    projects = sorted(db.list_projects(), key=lambda p: p["raised"] / max(p["goal"], 1), reverse=True)[:5]

    k = db.kpis()
    kpi_strip = ft.Row(
        [
            ft.Container(kpi_card("Total Volume", T.fmt_money(k["total_funds"]), ft.Icons.NORTH_EAST,
                                  delta="+12.5%", delta_positive=True), expand=1),
            ft.Container(kpi_card("Active Projects", str(k["active"]), ft.Icons.WORK_OUTLINE,
                                  delta="+2", delta_positive=True), expand=1),
            ft.Container(kpi_card("Donor Base", f"{k['donors']:,}", ft.Icons.PEOPLE_OUTLINE,
                                  delta="+48", delta_positive=True), expand=1),
            ft.Container(kpi_card("Pending Verifications", str(k["pending"]), ft.Icons.SCHEDULE,
                                  delta="-14", delta_positive=False,
                                  icon_bg="#FEF3C7", icon_fg=T.WARNING), expand=1),
        ],
        spacing=14,
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            T.section_title("Reports & Analytics", size=24),
                            T.subtitle("Drill into volume, status distribution, and category mix; export anything to CSV."),
                        ],
                        spacing=4, expand=True,
                    ),
                    T.primary_button("Generate Dashboard Report", icon=ft.Icons.INSERT_DRIVE_FILE_OUTLINED,
                                     on_click=lambda e: on_export_dashboard()),
                ],
            ),
            ft.Container(height=18),
            kpi_strip,
            ft.Container(height=18),
            ft.Row(
                [
                    _stat_card(
                        "Donation Volume — last 6 months",
                        f"Total ${sum(trend_values):,.0f} contributed across the period.",
                        ft.Container(content=line_chart(trend_labels, trend_values, height=240), height=240),
                    ),
                    _stat_card(
                        "Status Distribution",
                        "Verified vs Pending vs Failed across all transactions.",
                        ft.Container(content=bar_chart(status_keys, status_values, height=240), height=240),
                    ),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(height=18),
            ft.Row(
                [
                    _stat_card(
                        "Category Mix",
                        f"Funds raised by category across {len(by_cat)} categories.",
                        ft.Container(content=bar_chart(cat_labels, cat_values, height=220, color="#10B981"), height=220),
                    ),
                    _stat_card(
                        "Top Performing Projects",
                        "Projects ranked by % of goal achieved.",
                        ft.Column(
                            [progress_row(p["name"], p["raised"], p["goal"]) for p in projects] or
                            [ft.Text("No projects yet.", color=T.TEXT_MUTED)],
                            spacing=14,
                        ),
                    ),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(height=18),
            T.card(
                ft.Column(
                    [
                        T.section_title("Exports", size=16),
                        T.subtitle("Save data slices to /exports/ as CSV or text."),
                        ft.Container(height=14),
                        ft.Row(
                            [
                                ft.Container(_export_action("Donors CSV", "All donors with tier and totals.",
                                                            ft.Icons.PEOPLE_OUTLINE, lambda e: on_export_donors()), expand=1),
                                ft.Container(_export_action("Transactions CSV", "Every ledger entry, current filters ignored.",
                                                            ft.Icons.SWAP_HORIZ, lambda e: on_export_transactions()), expand=1),
                            ], spacing=12,
                        ),
                        ft.Container(height=12),
                        ft.Row(
                            [
                                ft.Container(_export_action("Projects CSV", "Project goals and status.",
                                                            ft.Icons.FOLDER_OUTLINED, lambda e: on_export_projects()), expand=1),
                                ft.Container(_export_action("Beneficiaries CSV", "Recipient progress and project links.",
                                                            ft.Icons.VOLUNTEER_ACTIVISM_OUTLINED, lambda e: on_export_beneficiaries()), expand=1),
                            ], spacing=12,
                        ),
                        ft.Container(height=12),
                        _export_action("Audit Report (text)", "Plain-text ledger summary suitable for printing.",
                                       ft.Icons.RECEIPT_LONG, lambda e: on_export_audit()),
                    ],
                    spacing=0,
                ),
                padding=20,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
