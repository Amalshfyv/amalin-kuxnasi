import flet as ft

from .. import db, theme as T
from ..components.cards import kpi_card, avatar_initials


STATUS_OPTIONS = ["All Statuses", "Active", "Pending", "On Hold"]
SORT_OPTIONS = ["Newest First", "Oldest First", "Name A-Z", "Funds High-Low"]


def _beneficiary_card(b, on_change_project):
    pct = (b["funds_received"] / b["funds_goal"] * 100) if b["funds_goal"] else 0
    project_label = b["project"] or "No active project assigned"
    cta = "Change Project" if b["project"] else "Assign to Project"
    bid = b["id"]

    cta_row = ft.Container(
        on_click=lambda e: on_change_project(b),
        ink=True,
        padding=ft.padding.symmetric(horizontal=4, vertical=2),
        content=ft.Row(
            [
                ft.Text(cta, size=12, color=T.PRIMARY, weight=ft.FontWeight.W_600),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.NORTH_EAST, color=T.PRIMARY, size=14),
            ]
        ),
    )
    return T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        avatar_initials(b["name"], size=36, bg=T.BG_CARD, fg=T.TEXT_SECONDARY),
                        ft.Container(width=10),
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(b["name"][:18], size=13, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                                        ft.Icon(ft.Icons.VERIFIED, color=T.PRIMARY, size=14),
                                    ],
                                    spacing=4,
                                ),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=12, color=T.TEXT_MUTED),
                                        ft.Text(b["location"] or "—", size=11, color=T.TEXT_MUTED),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_HORIZ,
                            items=[
                                ft.PopupMenuItem(text=cta, icon=ft.Icons.SWAP_HORIZ, on_click=lambda e: on_change_project(b)),
                            ],
                        ),
                    ]
                ),
                ft.Container(height=14),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Funds Status", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                                ft.Text(
                                    f"{T.fmt_money(b['funds_received'])} / {T.fmt_money(b['funds_goal'])}",
                                    size=12, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY,
                                ),
                            ],
                            spacing=2, expand=True,
                        ),
                        T.status_pill(b["status"] or "Active"),
                    ]
                ),
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Text("DISBURSEMENT PROGRESS", size=9, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                        ft.Container(expand=True),
                        ft.Text(f"{pct:.0f}%", size=11, weight=ft.FontWeight.W_700, color=T.PRIMARY),
                    ]
                ),
                ft.Container(height=4),
                ft.ProgressBar(
                    value=min(pct / 100, 1.0),
                    color=T.PRIMARY,
                    bgcolor=T.BG_CARD,
                    bar_height=5,
                    border_radius=999,
                ),
                ft.Container(height=12),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LINK, size=12, color=T.TEXT_MUTED),
                        ft.Text(f"Project: {project_label}" if b["project"] else project_label, size=11, color=T.TEXT_SECONDARY),
                    ],
                    spacing=4,
                ),
                ft.Container(height=12),
                T.divider(),
                ft.Container(height=10),
                cta_row,
            ],
            spacing=0,
        ),
        padding=18,
    )


def _kpi_strip():
    cards = [
        kpi_card("Total Recipients", str(len(db.list_beneficiaries())), ft.Icons.GROUP_OUTLINED),
        kpi_card("Pending Verification", str(sum(1 for b in db.list_beneficiaries() if b["status"] == "Pending")),
                 ft.Icons.ERROR_OUTLINE, icon_bg=T.WARNING_BG, icon_fg=T.WARNING),
        kpi_card("Total Disbursed", T.fmt_money_k(sum(b["funds_received"] for b in db.list_beneficiaries())),
                 ft.Icons.CHECK_CIRCLE_OUTLINE, icon_bg=T.SUCCESS_BG, icon_fg=T.SUCCESS),
        kpi_card("Active Links", str(sum(1 for b in db.list_beneficiaries() if b["project"])),
             ft.Icons.LINK, icon_bg=T.TIER_PLATINUM_BG, icon_fg=T.TIER_PLATINUM_FG),
    ]
    return ft.Row([ft.Container(c, expand=1) for c in cards], spacing=14)


def _filter(rows, search, status, sort):
    s = (search or "").strip().lower()
    out = list(rows)
    if status and status != "All Statuses":
        out = [b for b in out if b["status"] == status]
    if s:
        out = [b for b in out if s in (b["name"] or "").lower()
               or s in (b["location"] or "").lower()
               or s in (b["project"] or "").lower()]
    if sort == "Oldest First":
        out.sort(key=lambda b: b["id"])
    elif sort == "Name A-Z":
        out.sort(key=lambda b: (b["name"] or "").lower())
    elif sort == "Funds High-Low":
        out.sort(key=lambda b: b["funds_received"], reverse=True)
    else:
        out.sort(key=lambda b: b["id"], reverse=True)
    return out


def view(search_value, status_filter, sort, on_search, on_status_filter, on_sort,
         on_add, on_change_project, on_filter_btn):
    beneficiaries = _filter(db.list_beneficiaries(), search_value, status_filter, sort)
    cards = [_beneficiary_card(b, on_change_project) for b in beneficiaries]

    grid_rows = []
    per_row = 3
    for i in range(0, len(cards), per_row):
        chunk = cards[i:i + per_row]
        while len(chunk) < per_row:
            chunk.append(ft.Container(expand=1))
        grid_rows.append(
            ft.Row(
                [ft.Container(c, expand=1) for c in chunk],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    search_field = ft.TextField(
        value=search_value or "",
        hint_text="Search beneficiaries by name, location, or project...",
        prefix_icon=ft.Icons.SEARCH,
        border=ft.InputBorder.OUTLINE,
        border_color=T.BORDER,
        border_radius=8,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=10),
        height=44,
        expand=True,
        on_submit=lambda e: on_search(e.control.value),
    )
    status_dd = ft.Dropdown(
        value=status_filter or "All Statuses",
        options=[ft.dropdown.Option(s) for s in STATUS_OPTIONS],
        border_color=T.BORDER, border_radius=8, text_size=13,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        width=160,
        on_change=lambda e: on_status_filter(e.control.value),
    )
    sort_dd = ft.Dropdown(
        value=sort or "Newest First",
        options=[ft.dropdown.Option(s) for s in SORT_OPTIONS],
        border_color=T.BORDER, border_radius=8, text_size=13,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        width=160,
        on_change=lambda e: on_sort(e.control.value),
    )

    search_bar = T.card(
        ft.Row(
            [search_field, status_dd, sort_dd],
            spacing=10,
        ),
        padding=14,
    )

    body_grid = ft.Column(
        [r for pair in zip(grid_rows, [ft.Container(height=14)] * len(grid_rows)) for r in pair][:-1] if grid_rows else
        [ft.Container(padding=ft.padding.all(40),
                      content=ft.Text("No beneficiaries match the current filters.", color=T.TEXT_MUTED, size=12),
                      alignment=ft.alignment.center)],
        spacing=0,
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            T.section_title("Beneficiaries", size=24),
                            T.subtitle("Manage recipient entities, track verification status, and link them to active projects."),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    T.primary_button("Add Beneficiary", icon=ft.Icons.ADD, on_click=on_add),
                ],
            ),
            ft.Container(height=18),
            _kpi_strip(),
            ft.Container(height=18),
            search_bar,
            ft.Container(height=18),
            body_grid,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
