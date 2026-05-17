import flet as ft

from .. import db, theme as T
from ..components.cards import progress_row
from ..components.charts import bar_chart


STATUS_OPTIONS = ["All", "In Progress", "Pending", "On Hold", "Verified", "Archived"]


def _project_row(p, on_open):
    pid = p["id"]
    return ft.Container(
        on_click=lambda e: on_open(pid),
        ink=True,
        padding=ft.padding.symmetric(horizontal=16, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, T.DIVIDER)),
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.FOLDER_OUTLINED, size=18, color=T.PRIMARY),
                    width=36,
                    height=36,
                    bgcolor=T.PRIMARY_LIGHT,
                    border_radius=8,
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    [
                        ft.Text(p["name"], size=14, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                        ft.Row(
                            [
                                ft.Text(p["category"] or "—", size=12, color=T.TEXT_MUTED),
                                ft.Text(p["id"], size=11, color=T.TEXT_MUTED),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Column(
                    [progress_row("", p["raised"], p["goal"])],
                    width=260,
                ),
                T.status_pill(p["status"] or "Active"),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=T.TEXT_MUTED),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def _filter_results(rows, search, status):
    s = (search or "").strip().lower()
    out = []
    for r in rows:
        if status and status != "All" and (r.get("status") or "") != status:
            continue
        if s and not (
            s in (r.get("name") or "").lower()
            or s in (r.get("category") or "").lower()
            or s in (r.get("id") or "").lower()
        ):
            continue
        out.append(r)
    return out


def view(search_value, status_filter, on_search, on_status_filter, on_open_project, on_new_project):
    projects = db.list_projects()
    visible = _filter_results(projects, search_value, status_filter)

    search_field = ft.TextField(
        value=search_value or "",
        hint_text="Search projects",
        prefix_icon=ft.Icons.SEARCH,
        border=ft.InputBorder.OUTLINE,
        border_color=T.BORDER,
        border_radius=8,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=10),
        height=40,
        width=240,
        on_submit=lambda e: on_search(e.control.value),
    )
    status_dd = ft.Dropdown(
        value=status_filter or "All",
        options=[ft.dropdown.Option(s) for s in STATUS_OPTIONS],
        border_color=T.BORDER,
        border_radius=8,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        width=160,
        on_change=lambda e: on_status_filter(e.control.value),
    )

    rows = [_project_row(p, on_open_project) for p in visible] or [
        ft.Container(padding=ft.padding.all(28),
                     content=ft.Text("No projects match the current filters.", color=T.TEXT_MUTED, size=12),
                     alignment=ft.alignment.center)
    ]

    table = T.card(
        ft.Column(
            [
                ft.Container(
                    padding=ft.padding.all(16),
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    T.section_title("Project Management", size=18),
                                    T.subtitle(f"{len(visible)} of {len(projects)} projects shown."),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            search_field,
                            ft.Container(width=10),
                            status_dd,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                T.divider(),
                ft.Column(rows, spacing=0),
            ],
            spacing=0,
        ),
        padding=0,
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            T.section_title("Project Management", size=24),
                            T.subtitle("Track progress, funding, and verification status across all initiatives."),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    T.primary_button("New Project", icon=ft.Icons.ADD, on_click=on_new_project),
                ],
            ),
            ft.Container(height=18),
            table,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _meta_box(label, value):
    return ft.Container(
        padding=ft.padding.all(12),
        border=ft.border.all(1, T.BORDER),
        border_radius=8,
        expand=True,
        content=ft.Column(
            [
                ft.Text(label.upper(), size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                ft.Container(height=4),
                ft.Text(value, size=13, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_700),
            ],
            spacing=0,
        ),
    )


def _section_label(text):
    return ft.Text(text, size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700)


def project_drawer_panel(project, on_close, on_edit, on_full_ledger, on_archive):
    trend = db.project_funding_trend(project["id"])
    if not trend:
        labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        values = [22000, 28000, 18000, 38000, 30000, 42000]
    else:
        labels = [r["month"] for r in trend]
        values = [r["amount"] for r in trend]

    leads = (project.get("leads") or "").split(",")
    leads = [l.strip() for l in leads if l.strip()]
    if len(leads) > 3:
        visible = leads[:3]
        extra = f"+{len(leads) - 3}"
    else:
        visible, extra = leads, None

    lead_avatars = []
    for i, l in enumerate(visible):
        lead_avatars.append(
            ft.Container(
                content=ft.Text(l, size=10, weight=ft.FontWeight.W_700, color=T.TEXT_SECONDARY),
                width=28,
                height=28,
                bgcolor="#E5E7EB",
                border_radius=999,
                alignment=ft.alignment.center,
                margin=ft.margin.only(left=-8 if i > 0 else 0),
            )
        )
    if extra:
        lead_avatars.append(
            ft.Container(
                content=ft.Text(extra, size=10, weight=ft.FontWeight.W_700, color=T.TEXT_SECONDARY),
                width=28,
                height=28,
                bgcolor="#E5E7EB",
                border_radius=999,
                alignment=ft.alignment.center,
                margin=ft.margin.only(left=-8),
            )
        )

    more_menu = ft.PopupMenuButton(
        icon=ft.Icons.MORE_HORIZ,
        items=[
            ft.PopupMenuItem(text="Edit Project", icon=ft.Icons.EDIT, on_click=lambda e: on_edit(project["id"])),
            ft.PopupMenuItem(text="View Full Ledger", icon=ft.Icons.OPEN_IN_NEW, on_click=lambda e: on_full_ledger(project["id"])),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="Archive Project", icon=ft.Icons.ARCHIVE_OUTLINED, on_click=lambda e: on_archive(project["id"])),
        ],
    )

    return ft.Container(
        width=420,
        height=820,
        bgcolor=ft.colors.ON_PRIMARY,
        padding=ft.padding.all(24),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(project["name"] + (f": Sahel" if project["id"] == "PRJ-001" else ""), size=18, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                                ft.Text(f"ID: {project['id']}", size=12, color=T.TEXT_MUTED),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        more_menu,
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=18, icon_color=T.TEXT_MUTED, on_click=lambda e: on_close()),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=8),
                ft.Row(
                    [
                        _section_label("STATUS & META"),
                        ft.Container(expand=True),
                        T.status_pill(project["status"] or "In Progress"),
                    ]
                ),
                ft.Container(height=10),
                ft.Row(
                    [
                        _meta_box("Category", project["category"] or "—"),
                        ft.Container(width=10),
                        _meta_box("Last Update", project["last_update"] or "—"),
                    ]
                ),
                ft.Container(height=18),
                _section_label("FUNDING MOMENTUM"),
                ft.Container(height=8),
                ft.Container(content=bar_chart(labels, values, height=160), height=160),
                ft.Container(height=18),
                _section_label("DESCRIPTION"),
                ft.Container(height=8),
                ft.Container(
                    padding=ft.padding.all(12),
                    border=ft.border.all(1, T.BORDER),
                    border_radius=8,
                    content=ft.Text(
                        f"\"{project['description']}\"",
                        size=12,
                        color=T.TEXT_SECONDARY,
                        italic=True,
                    ),
                ),
                ft.Container(height=18),
                _section_label("PROJECT LEADS"),
                ft.Container(height=8),
                ft.Row(lead_avatars, spacing=0),
                ft.Container(expand=True),
                ft.Row(
                    [
                        T.primary_button("Edit Project", on_click=lambda e: on_edit(project["id"]), expand=True),
                        ft.Container(width=10),
                        T.outline_button("View Full Ledger", on_click=lambda e: on_full_ledger(project["id"]), expand=True),
                    ]
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            expand=True,
        ),
    )
