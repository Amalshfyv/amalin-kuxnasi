"""Reusable form, confirm, and info dialogs."""
from __future__ import annotations
import flet as ft

from . import theme as T


def _input(label: str, value: str = "", hint: str = "", multiline: bool = False, prefix: str = ""):
    return ft.TextField(
        label=label,
        value=value,
        hint_text=hint,
        prefix_text=prefix,
        multiline=multiline,
        min_lines=3 if multiline else 1,
        max_lines=6 if multiline else 1,
        border=ft.InputBorder.OUTLINE,
        border_color=T.BORDER,
        border_radius=8,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=12),
    )


def _dropdown(label: str, options: list, value=None):
    return ft.Dropdown(
        label=label,
        value=value,
        options=[ft.dropdown.Option(o) for o in options],
        border_color=T.BORDER,
        border_radius=8,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=12),
    )


def _dialog_shell(title: str, subtitle: str, body: ft.Control, primary_label: str,
                  on_primary, on_close, width: int = 480, secondary_label: str = "Cancel"):
    return ft.AlertDialog(
        modal=True,
        bgcolor=ft.colors.ON_PRIMARY,
        shape=ft.RoundedRectangleBorder(radius=14),
        content_padding=0,
        content=ft.Container(
            width=width,
            padding=ft.padding.all(24),
            content=ft.Column(
                [
                    ft.Text(title, size=18, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                    ft.Text(subtitle, size=12, color=T.TEXT_MUTED),
                    ft.Container(height=14),
                    body,
                    ft.Container(height=18),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            T.outline_button(secondary_label, on_click=lambda e: on_close()),
                            ft.Container(width=10),
                            T.primary_button(primary_label, on_click=lambda e: on_primary()),
                        ],
                    ),
                ],
                spacing=2,
            ),
        ),
    )


def project_form(existing: dict | None, on_save, on_close):
    name_f = _input("Project Name", value=(existing or {}).get("name", ""))
    cat_f = _dropdown("Category", ["Environment", "Education", "Humanitarian", "Health", "Animal Welfare"],
                     value=(existing or {}).get("category", "Environment"))
    goal_f = _input("Funding Goal (USD)", value=str(int((existing or {}).get("goal", 50000))), prefix="$ ")
    desc_f = _input("Description", value=(existing or {}).get("description", ""), multiline=True)
    status_f = _dropdown("Status", ["In Progress", "Pending", "On Hold", "Verified"],
                         value=(existing or {}).get("status", "In Progress"))

    body = ft.Column(
        [
            name_f,
            ft.Container(height=10),
            ft.Row([ft.Container(cat_f, expand=1), ft.Container(width=10), ft.Container(goal_f, expand=1)]),
            ft.Container(height=10),
            status_f,
            ft.Container(height=10),
            desc_f,
        ],
        spacing=0,
    )

    def submit():
        if not (name_f.value or "").strip():
            name_f.error_text = "Required"
            name_f.update()
            return
        try:
            goal = float((goal_f.value or "0").replace(",", ""))
        except ValueError:
            goal = 0
        on_save({
            "id": (existing or {}).get("id"),
            "name": name_f.value.strip(),
            "category": cat_f.value or "",
            "goal": goal,
            "status": status_f.value or "In Progress",
            "description": (desc_f.value or "").strip(),
        })

    title = "Edit Project" if existing else "New Project"
    sub = "Update the details below." if existing else "Define a new initiative to start collecting donations."
    return _dialog_shell(title, sub, body, "Save", submit, on_close, width=520)


def beneficiary_form(projects: list, on_save, on_close):
    name_f = _input("Beneficiary / Organization")
    loc_f = _input("Location")
    goal_f = _input("Funds Goal (USD)", value="10000", prefix="$ ")
    proj_f = _dropdown("Linked Project", [""] + [p["name"] for p in projects], value="")

    body = ft.Column(
        [
            name_f,
            ft.Container(height=10),
            loc_f,
            ft.Container(height=10),
            ft.Row([ft.Container(goal_f, expand=1), ft.Container(width=10), ft.Container(proj_f, expand=1)]),
        ],
        spacing=0,
    )

    def submit():
        if not (name_f.value or "").strip():
            name_f.error_text = "Required"
            name_f.update()
            return
        try:
            goal = float((goal_f.value or "0").replace(",", ""))
        except ValueError:
            goal = 0
        on_save({
            "name": name_f.value.strip(),
            "location": (loc_f.value or "").strip(),
            "funds_goal": goal,
            "project": proj_f.value or "",
        })

    return _dialog_shell("Add Beneficiary", "Register a new recipient and optionally link a project.", body, "Add", submit, on_close, width=520)


def change_project_dialog(beneficiary: dict, projects: list, on_save, on_close):
    current = beneficiary.get("project") or ""
    proj_f = _dropdown("Linked Project", ["(none)"] + [p["name"] for p in projects], value=current or "(none)")
    body = ft.Column(
        [
            ft.Text(f"Beneficiary: {beneficiary['name']}", size=13, weight=ft.FontWeight.W_600),
            ft.Container(height=10),
            proj_f,
        ],
        spacing=0,
    )

    def submit():
        v = proj_f.value or "(none)"
        on_save("" if v == "(none)" else v)

    title = "Change Project" if current else "Assign to Project"
    return _dialog_shell(title, "Select a project to link this beneficiary to.", body, "Save", submit, on_close, width=460)


def broadcast_dialog(donors: list, on_send, on_close):
    audience_options = ["All donors", "Platinum tier", "Gold tier", "Silver tier", "Bronze tier"]
    aud_f = _dropdown("Audience", audience_options, value="All donors")
    subj_f = _input("Subject", value="An update from Charity Transparency Ledger")
    body_f = _input("Message", multiline=True,
                    value="Thank you for your continued support. Here's our latest progress on the projects you've helped fund...")

    counts = {
        "All donors": len(donors),
        "Platinum tier": sum(1 for d in donors if d["tier"] == "Platinum"),
        "Gold tier": sum(1 for d in donors if d["tier"] == "Gold"),
        "Silver tier": sum(1 for d in donors if d["tier"] == "Silver"),
        "Bronze tier": sum(1 for d in donors if d["tier"] == "Bronze"),
    }
    recipient_count = ft.Text(f"Recipients: {counts['All donors']}", size=11, color=T.TEXT_MUTED)

    def on_aud_change(e):
        recipient_count.value = f"Recipients: {counts.get(aud_f.value, 0)}"
        recipient_count.update()
    aud_f.on_change = on_aud_change

    body = ft.Column(
        [
            aud_f,
            ft.Container(height=4),
            recipient_count,
            ft.Container(height=10),
            subj_f,
            ft.Container(height=10),
            body_f,
        ],
        spacing=0,
    )

    def submit():
        on_send({
            "audience": aud_f.value or "All donors",
            "audience_count": counts.get(aud_f.value, 0),
            "subject": (subj_f.value or "").strip(),
            "body": (body_f.value or "").strip(),
        })

    return _dialog_shell("Broadcast Message", "Compose an update for your donor community.", body, "Send", submit, on_close, width=560)


def confirm_dialog(title: str, message: str, on_confirm, on_close, danger: bool = False, confirm_label: str = "Confirm"):
    body = ft.Text(message, size=13, color=T.TEXT_SECONDARY)
    dlg = ft.AlertDialog(
        modal=True,
        bgcolor=ft.colors.ON_PRIMARY,
        shape=ft.RoundedRectangleBorder(radius=14),
        content_padding=0,
        content=ft.Container(
            width=420,
            padding=ft.padding.all(22),
            content=ft.Column(
                [
                    ft.Text(title, size=16, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                    ft.Container(height=8),
                    body,
                    ft.Container(height=18),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            T.outline_button("Cancel", on_click=lambda e: on_close()),
                            ft.Container(width=10),
                            ft.ElevatedButton(
                                confirm_label,
                                on_click=lambda e: on_confirm(),
                                style=ft.ButtonStyle(
                                    bgcolor=T.DANGER if danger else T.PRIMARY,
                                    color=ft.colors.ON_PRIMARY,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    elevation=0,
                                    padding=ft.padding.symmetric(horizontal=18, vertical=10),
                                    text_style=ft.TextStyle(weight=ft.FontWeight.W_600, size=13),
                                ),
                            ),
                        ],
                    ),
                ],
                spacing=0,
            ),
        ),
    )
    return dlg


def info_dialog(title: str, body_control: ft.Control, on_close, width: int = 520):
    return ft.AlertDialog(
        modal=True,
        bgcolor=ft.colors.ON_PRIMARY,
        shape=ft.RoundedRectangleBorder(radius=14),
        content_padding=0,
        content=ft.Container(
            width=width,
            padding=ft.padding.all(22),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(title, size=16, weight=ft.FontWeight.W_700, expand=True),
                            ft.IconButton(icon=ft.Icons.CLOSE, icon_size=18, on_click=lambda e: on_close()),
                        ],
                    ),
                    ft.Container(height=8),
                    body_control,
                    ft.Container(height=18),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            T.primary_button("Close", on_click=lambda e: on_close()),
                        ],
                    ),
                ],
                spacing=0,
            ),
        ),
    )


def notifications_popup(items: list, on_close, on_clear):
    rows = []
    for it in items:
        rows.append(
            ft.Container(
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                border=ft.border.only(bottom=ft.BorderSide(1, T.DIVIDER)),
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(it["icon"], size=14, color=it["color"]),
                            width=28, height=28,
                            bgcolor=it.get("bg") or T.PRIMARY_LIGHT,
                            border_radius=999, alignment=ft.alignment.center,
                        ),
                        ft.Column(
                            [
                                ft.Text(it["title"], size=12, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                                ft.Text(it["body"], size=11, color=T.TEXT_SECONDARY),
                            ],
                            spacing=2, expand=True,
                        ),
                        ft.Text(it["when"], size=10, color=T.TEXT_MUTED),
                    ],
                    spacing=10,
                ),
            )
        )
    list_col = ft.Column(rows, spacing=0, scroll=ft.ScrollMode.AUTO, height=360) if rows else \
        ft.Container(padding=20, content=ft.Text("No notifications.", size=12, color=T.TEXT_MUTED), alignment=ft.alignment.center)

    return ft.AlertDialog(
        modal=True,
        bgcolor=ft.colors.ON_PRIMARY,
        shape=ft.RoundedRectangleBorder(radius=14),
        content_padding=0,
        content=ft.Container(
            width=440,
            padding=ft.padding.all(0),
            content=ft.Column(
                [
                    ft.Container(
                        padding=ft.padding.all(14),
                        border=ft.border.only(bottom=ft.BorderSide(1, T.DIVIDER)),
                        content=ft.Row(
                            [
                                ft.Text("Notifications", size=14, weight=ft.FontWeight.W_700, expand=True),
                                ft.TextButton("Clear all", on_click=lambda e: on_clear(), style=ft.ButtonStyle(color=T.TEXT_MUTED)),
                                ft.IconButton(icon=ft.Icons.CLOSE, icon_size=18, on_click=lambda e: on_close()),
                            ],
                        ),
                    ),
                    list_col,
                ],
                spacing=0,
            ),
        ),
    )
