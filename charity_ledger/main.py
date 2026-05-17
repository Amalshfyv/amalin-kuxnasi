"""Charity Transparency Ledger — Flet desktop/web app."""
from __future__ import annotations
import sys
import webbrowser
from pathlib import Path
from typing import Optional
import flet as ft

# Compatibility shim: some flet versions do not expose `colors` on the top-level
# object. Older code in this repo references `ft.colors.<NAME>`. Define a minimal
# fallback here so the app remains compatible with multiple flet releases.
if not hasattr(ft, "colors"):
    class _FletColors:
        PRIMARY = "#1976D2"
        PRIMARY_CONTAINER = "#E3F2FD"
        ON_PRIMARY = "#FFFFFF"

    ft.colors = _FletColors()


def _sync_ft_colors():
    if not hasattr(ft, "colors"):
        return
    for attr in ("PRIMARY", "PRIMARY_CONTAINER", "ON_PRIMARY"):
        try:
            setattr(ft.colors, attr, getattr(T, attr))
        except Exception:
            pass


# Ensure the colors shim stays in sync with the current theme values.
_sync_ft_colors()

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from charity_ledger import db, theme as T, dialogs, exports
    from charity_ledger.components.shell import shell
    from charity_ledger.views import (
        dashboard,
        projects as projects_view,
        donors as donors_view,
        beneficiaries as beneficiaries_view,
        transactions as transactions_view,
        public_project,
        donate_flow as donate_flow_view,
        reports as reports_view,
        settings as settings_view,
        admin_login,
    )
else:
    from . import db, theme as T, dialogs, exports
    from .components.shell import shell
    from .views import (
        dashboard,
        projects as projects_view,
        donors as donors_view,
        beneficiaries as beneficiaries_view,
        transactions as transactions_view,
        public_project,
        donate_flow as donate_flow_view,
        reports as reports_view,
        settings as settings_view,
        admin_login,
    )


class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.active = "dashboard"
        self.selected_donor_id: Optional[int] = None
        self.donate_flow = None
        self._open_dialogs: list = []

        # filters / search state
        self.project_search = ""
        self.project_status_filter = "All"
        self.donor_tier_filter = "All"
        self.donor_search = ""
        self.beneficiary_search = ""
        self.beneficiary_status_filter = "All"
        self.beneficiary_sort = "Newest First"
        self.tx_status_filter = "All"
        self.tx_search = ""
        self.global_search = ""

        # in-memory notifications + settings
        self.notifications = self._seed_notifications()
        self.settings = {
            "theme": "Light",
            "notifications_email": True,
            "notifications_push": False,
            "auto_verify": True,
        }
        self._configure_page()

    def _seed_notifications(self):
        return [
            {"icon": ft.Icons.CHECK_CIRCLE, "color": T.SUCCESS, "bg": T.SUCCESS_BG,
             "title": "New donation verified",
             "body": "Sarah Jenkins contributed $2,500 to Clean Water Initiative.",
             "when": "2h"},
            {"icon": ft.Icons.SCHEDULE, "color": T.WARNING, "bg": T.WARNING_BG,
             "title": "Pending verification",
             "body": "TX-8842 from Michael Chen awaiting payment provider response.",
             "when": "5h"},
            {"icon": ft.Icons.PERSON_ADD, "color": T.PRIMARY, "bg": T.PRIMARY_LIGHT,
             "title": "New donor onboarded",
             "body": "Amina Okafor joined the Platinum tier.",
             "when": "1d"},
            {"icon": ft.Icons.ERROR_OUTLINE, "color": T.DANGER, "bg": T.DANGER_BG,
             "title": "Failed transaction",
             "body": "TX-8750 declined by payment processor.",
             "when": "2d"},
        ]

    def _configure_page(self):
        self.page.title = "Charity Transparency Ledger"
        self.page.bgcolor = T.BG_APP
        self.page.padding = 0
        self.page.spacing = 0
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.theme_mode = ft.ThemeMode.LIGHT
        # Ensure theme module values match the current settings before applying the page theme
        try:
            T.apply_theme(self.settings.get("theme", "Light"))
        except Exception:
            pass
        _sync_ft_colors()
        self.page.theme = ft.Theme(
            color_scheme_seed=T.PRIMARY,
            font_family="Inter",
        )
        self.page.window.width = 1380
        self.page.window.height = 900
        self.page.window.min_width = 1100
        self.page.window.min_height = 720

    # ---------- routing ----------
    def go(self, route: str):
        self.current_route = route
        self._render_route()
        if self.page.route != route:
            try:
                self.page.route = route
                self.page.update()
            except Exception:
                pass

    def _render_route(self):
        route = getattr(self, "current_route", "/dashboard")
        if route in ("/", "/dashboard"):
            self.active = "dashboard"
            content = self._wrap_admin(self._dashboard_body())
        elif route == "/projects":
            self.active = "projects"
            content = self._wrap_admin(self._projects_body())
        elif route == "/donors":
            self.active = "donors"
            content = self._wrap_admin(self._donors_body())
        elif route == "/beneficiaries":
            self.active = "beneficiaries"
            content = self._wrap_admin(self._beneficiaries_body())
        elif route == "/transactions":
            self.active = "transactions"
            content = self._wrap_admin(self._transactions_body())
        elif route == "/reports":
            self.active = "reports"
            content = self._wrap_admin(reports_view.view(
                on_export_dashboard=self._export_dashboard_report,
                on_export_donors=lambda: self._do_export(exports.export_donors, "donors"),
                on_export_transactions=lambda: self._do_export(exports.export_transactions, "transactions"),
                on_export_projects=lambda: self._do_export(exports.export_projects, "projects"),
                on_export_beneficiaries=lambda: self._do_export(exports.export_beneficiaries, "beneficiaries"),
                on_export_audit=lambda: self._do_export(exports.export_audit_report, "audit report"),
            ))
        elif route == "/settings":
            self.active = "settings"
            content = self._wrap_admin(settings_view.view(
                self.settings,
                on_save=self._save_settings,
                on_reseed=self._reseed_data,
            ))
        elif route.startswith("/public/project"):
            pid = route.split("/")[-1] if "/" in route else "PRJ-001"
            if not pid.startswith("PRJ"):
                pid = "PRJ-001"
            content = public_project.view(
                pid,
                on_donate=lambda *e: self.go("/donate"),
                on_admin_login=lambda *e: self.go("/admin/login"),
                on_download_audit=lambda *e: self._do_export(lambda: exports.export_audit_report(pid), f"audit report for {pid}"),
                on_view_history=lambda *e: self.go("/transactions"),
                on_learn_more=self._scroll_to_mission,
            )
        elif route == "/admin/login":
            content = admin_login.view(
                self.page,
                on_login_success=lambda: self.go("/dashboard"),
                on_back=lambda: self.go("/public/project/PRJ-001"),
            )
        elif route == "/donate":
            self.donate_flow = donate_flow_view.DonateFlow(
                self.page,
                on_admin_login=lambda *e: self.go("/admin/login"),
                on_finish=lambda *e: self.go("/public/project/PRJ-001"),
            )
            content = self.donate_flow.render()
        else:
            self.active = "dashboard"
            content = self._wrap_admin(self._dashboard_body())
        self.page.controls.clear()
        self.page.add(content)

    def _wrap_admin(self, body):
        return shell(
            self.active,
            body,
            on_nav=self._nav,
            on_public_view=lambda: self.go("/public/project/PRJ-001"),
            on_logout=self._logout,
            on_settings=lambda: self.go("/settings"),
            on_search_change=self._on_global_search,
            on_search_value=self.global_search,
            on_bell_click=self._open_notifications,
            notif_count=len(self.notifications),
        )

    # ---------- navigation ----------
    def _nav(self, key: str):
        self.go(f"/{key}")

    def _logout(self):
        self.go("/public/project/PRJ-001")
        self._snack("Signed out — viewing public ledger.")

    # ---------- bodies ----------
    def _dashboard_body(self):
        return dashboard.view(
            on_nav=self._nav,
            on_new_project=lambda e: self._open_new_project(),
            on_view_all_projects=lambda: self.go("/projects"),
            on_audit_tx=self._open_audit,
            on_generate_report=lambda e: self._export_dashboard_report(),
            on_audit_ledger=lambda e: self.go("/transactions"),
            on_full_analysis=lambda e: self.go("/reports"),
        )

    def _projects_body(self):
        return projects_view.view(
            search_value=self.project_search,
            status_filter=self.project_status_filter,
            on_search=self._on_project_search,
            on_status_filter=self._on_project_filter,
            on_open_project=self._open_project_drawer,
            on_new_project=lambda e: self._open_new_project(),
        )

    def _donors_body(self):
        return donors_view.view(
            self._select_donor,
            self.selected_donor_id,
            tier_filter=self.donor_tier_filter,
            on_tier_filter=self._on_donor_tier_filter,
            on_export=lambda e: self._do_export(exports.export_donors, "donors"),
            on_broadcast=lambda e: self._open_broadcast(),
            on_donor_action=self._donor_row_action,
            on_full_profile=self._open_donor_profile,
            on_phone=self._copy_phone,
        )

    def _beneficiaries_body(self):
        return beneficiaries_view.view(
            search_value=self.beneficiary_search,
            status_filter=self.beneficiary_status_filter,
            sort=self.beneficiary_sort,
            on_search=self._on_beneficiary_search,
            on_status_filter=self._on_beneficiary_status,
            on_sort=self._on_beneficiary_sort,
            on_add=lambda e: self._open_add_beneficiary(),
            on_change_project=self._open_change_project,
            on_filter_btn=lambda e: self._snack("Filter row available below the header."),
        )

    def _transactions_body(self):
        return transactions_view.view(
            on_audit=self._open_audit,
            search_value=self.tx_search,
            status_filter=self.tx_status_filter,
            on_search=self._on_tx_search,
            on_status_filter=self._on_tx_filter,
            on_export=lambda e: self._do_export(
                lambda: exports.export_transactions(None if self.tx_status_filter == "All" else self.tx_status_filter),
                f"transactions ({self.tx_status_filter})",
            ),
            on_audit_ledger=lambda e: self._do_export(exports.export_audit_report, "ledger audit report"),
            on_tx_action=self._tx_row_action,
        )

    # ---------- search/filter handlers ----------
    def _on_project_search(self, v: str):
        self.project_search = v
        self.go("/projects")

    def _on_project_filter(self, v: str):
        self.project_status_filter = v
        self.go("/projects")

    def _on_donor_tier_filter(self, v: str):
        self.donor_tier_filter = v
        self.go("/donors")

    def _on_beneficiary_search(self, v: str):
        self.beneficiary_search = v
        self.go("/beneficiaries")

    def _on_beneficiary_status(self, v: str):
        self.beneficiary_status_filter = v
        self.go("/beneficiaries")

    def _on_beneficiary_sort(self, v: str):
        self.beneficiary_sort = v
        self.go("/beneficiaries")

    def _on_tx_search(self, v: str):
        self.tx_search = v
        self.go("/transactions")

    def _on_tx_filter(self, v: str):
        self.tx_status_filter = v
        self.go("/transactions")

    def _on_global_search(self, v: str):
        self.global_search = v
        # Route to most relevant view based on search prefix.
        if v.startswith("TX-") or v.startswith("tx_"):
            self.tx_search = v
            self.go("/transactions")
        elif v.startswith("PRJ-"):
            self.project_search = v
            self.go("/projects")

    # ---------- selections ----------
    def _select_donor(self, donor_id: int):
        self.selected_donor_id = donor_id
        self.go("/donors")

    # ---------- dialogs / actions ----------
    def _open_new_project(self):
        dlg = dialogs.project_form(None, on_save=self._save_new_project, on_close=self._close_dialog)
        self._open(dlg)

    def _save_new_project(self, data: dict):
        data["id"] = db.next_project_id()
        db.insert_project(data)
        self._close_dialog()
        self.go("/projects")
        self._snack(f"Created project {data['id']} — {data['name']}.")

    def _open_edit_project(self, pid: str):
        proj = db.get_project(pid)
        if not proj:
            return
        # close drawer first if open
        if self._open_dialogs:
            self.page.close(self._open_dialogs[-1])
            self._open_dialogs.pop()
        dlg = dialogs.project_form(proj, on_save=self._save_edit_project, on_close=self._close_dialog)
        self._open(dlg)

    def _save_edit_project(self, data: dict):
        db.update_project(data)
        self._close_dialog()
        self.go("/projects")
        self._snack(f"Updated {data['name']}.")

    def _open_add_beneficiary(self):
        dlg = dialogs.beneficiary_form(db.list_projects(), on_save=self._save_beneficiary, on_close=self._close_dialog)
        self._open(dlg)

    def _save_beneficiary(self, data: dict):
        db.insert_beneficiary(data)
        self._close_dialog()
        self.go("/beneficiaries")
        self._snack(f"Added beneficiary: {data['name']}.")

    def _open_change_project(self, beneficiary: dict):
        dlg = dialogs.change_project_dialog(
            beneficiary,
            db.list_projects(),
            on_save=lambda new_proj: self._change_beneficiary_project(beneficiary["id"], new_proj),
            on_close=self._close_dialog,
        )
        self._open(dlg)

    def _change_beneficiary_project(self, bid: int, new_project: str):
        db.update_beneficiary_project(bid, new_project)
        self._close_dialog()
        self.go("/beneficiaries")
        msg = f"Linked to {new_project}." if new_project else "Project link removed."
        self._snack(msg)

    def _open_broadcast(self):
        dlg = dialogs.broadcast_dialog(db.list_donors(), on_send=self._send_broadcast, on_close=self._close_dialog)
        self._open(dlg)

    def _send_broadcast(self, payload: dict):
        self._close_dialog()
        self.notifications.insert(0, {
            "icon": ft.Icons.CAMPAIGN, "color": T.PRIMARY, "bg": T.PRIMARY_LIGHT,
            "title": "Broadcast sent",
            "body": f"\"{payload['subject']}\" delivered to {payload['audience_count']} {payload['audience'].lower()}.",
            "when": "now",
        })
        self._snack(f"Sent to {payload['audience_count']} recipient(s) — {payload['audience']}.")

    def _open_donor_profile(self, donor_id: int):
        donor = next((d for d in db.list_donors() if d["id"] == donor_id), None)
        if not donor:
            return
        body = ft.Column(
            [
                ft.Text(donor["name"], size=20, weight=ft.FontWeight.W_700),
                ft.Container(height=4),
                ft.Text(donor["email"], size=12, color=T.TEXT_SECONDARY),
                ft.Container(height=14),
                _kv("Tier", donor["tier"]),
                _kv("Total Donated", T.fmt_money(donor["total_donated"], 2)),
                _kv("Location", donor["location"] or "—"),
                _kv("Joined", donor["joined"] or "—"),
                _kv("Phone", donor["phone"] or "—"),
                _kv("Projects Supported", str(donor["projects_supported"] or 0)),
                _kv("Last Activity", donor["last_activity"] or "—"),
            ],
            spacing=4,
        )
        dlg = dialogs.info_dialog(f"Donor Profile — {donor['name']}", body, on_close=self._close_dialog)
        self._open(dlg)

    def _copy_phone(self, donor_id: int):
        donor = next((d for d in db.list_donors() if d["id"] == donor_id), None)
        if donor and donor.get("phone"):
            try:
                self.page.set_clipboard(donor["phone"])
            except Exception:
                pass
            self._snack(f"Copied {donor['phone']} to clipboard.")
        else:
            self._snack("No phone number on file.")

    def _donor_row_action(self, donor_id: int, action: str):
        donor = next((d for d in db.list_donors() if d["id"] == donor_id), None)
        if not donor:
            return
        if action == "profile":
            self._open_donor_profile(donor_id)
        elif action == "message":
            self._snack(f"Drafting message to {donor['name']}…")
        elif action == "tier":
            self._snack(f"{donor['name']} is currently {donor['tier']}. Open profile to upgrade.")

    def _tx_row_action(self, tx_id: str, action: str):
        if action == "audit":
            self._open_audit(tx_id)
        elif action == "verify":
            db.update_transaction_status(tx_id, "Verified")
            self.go("/transactions")
            self._snack(f"{tx_id} marked verified.")
        elif action == "fail":
            db.update_transaction_status(tx_id, "Failed")
            self.go("/transactions")
            self._snack(f"{tx_id} marked failed.")
        elif action == "export":
            try:
                p = exports.export_single_transaction(tx_id)
                self._snack(f"Saved {p.name} to /exports/.")
            except Exception as ex:
                self._snack(f"Export failed: {ex}")
        elif action == "delete":
            self._open(dialogs.confirm_dialog(
                "Delete transaction?",
                f"This will remove {tx_id} from the ledger. This cannot be undone.",
                on_confirm=lambda: self._do_delete_tx(tx_id),
                on_close=self._close_dialog,
                danger=True,
                confirm_label="Delete",
            ))

    def _do_delete_tx(self, tx_id: str):
        db.delete_transaction(tx_id)
        self._close_dialog()
        self.go("/transactions")
        self._snack(f"Deleted {tx_id}.")

    # ---------- exports ----------
    def _do_export(self, fn, label: str):
        try:
            path = fn()
        except Exception as ex:
            self._snack(f"Export failed: {ex}")
            return
        self._open(dialogs.info_dialog(
            "Export ready",
            ft.Column(
                [
                    ft.Text(f"Exported {label}.", size=13),
                    ft.Container(height=8),
                    ft.Container(
                        padding=ft.padding.all(10),
                            bgcolor=T.BG_CARD,
                        border_radius=6,
                        content=ft.Text(str(path), size=11, color=T.TEXT_SECONDARY, selectable=True, font_family="Courier"),
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            T.outline_button("Open Folder", on_click=lambda e: self._open_folder(path.parent)),
                        ],
                    ),
                ],
                spacing=0,
            ),
            on_close=self._close_dialog,
        ))

    def _export_dashboard_report(self):
        self._do_export(exports.generate_dashboard_report, "dashboard report")

    def _open_folder(self, path):
        try:
            webbrowser.open(f"file://{path}")
        except Exception:
            pass

    # ---------- drawer / modals ----------
    def _open_project_drawer(self, pid: str):
        project = db.get_project(pid)
        if not project:
            return
        panel = projects_view.project_drawer_panel(
            project,
            on_close=self._close_dialog,
            on_edit=self._open_edit_project,
            on_full_ledger=lambda p: self.go(f"/public/project/{p}"),
            on_archive=self._archive_project,
        )
        dlg = ft.AlertDialog(
            modal=True,
            content=panel,
            content_padding=0,
            inset_padding=ft.padding.only(left=0, top=0, right=0, bottom=0),
            alignment=ft.alignment.center_right,
            bgcolor=T.BG_CARD,
            shape=ft.RoundedRectangleBorder(radius=0),
        )
        self._open(dlg)

    def _archive_project(self, pid: str):
        self._close_dialog()
        self._open(dialogs.confirm_dialog(
            "Archive project?",
            f"Archived projects stop accepting new contributions but keep the ledger intact.",
            on_confirm=lambda: self._do_archive_project(pid),
            on_close=self._close_dialog,
            danger=True,
            confirm_label="Archive",
        ))

    def _do_archive_project(self, pid: str):
        db.archive_project(pid)
        self._close_dialog()
        self.go("/projects")
        self._snack(f"{pid} archived.")

    def _open_audit(self, tx_id: str):
        tx = db.get_transaction(tx_id)
        if not tx:
            self._snack(f"Transaction {tx_id} not found")
            return
        dlg = transactions_view.audit_dialog(
            tx,
            on_close=self._close_dialog,
            on_export_csv=lambda tid: self._do_export(lambda: exports.export_single_transaction(tid), f"transaction {tid}"),
        )
        self._open(dlg)

    def _open_notifications(self):
        dlg = dialogs.notifications_popup(
            self.notifications,
            on_close=self._close_dialog,
            on_clear=self._clear_notifications,
        )
        self._open(dlg)

    def _clear_notifications(self):
        self.notifications = []
        self._close_dialog()
        self._snack("All notifications cleared.")
        self._render_route()

    # ---------- settings ----------
    def _save_settings(self, new_settings: dict):
        self.settings.update(new_settings)
        theme_choice = new_settings.get("theme")
        if theme_choice == "Dark":
            T.apply_theme("Dark")
            self.page.theme_mode = ft.ThemeMode.DARK
        elif theme_choice == "Light":
            T.apply_theme("Light")
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            # System - let the OS decide; keep current module colors in sync with theme_mode
            T.apply_theme("Light")
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        _sync_ft_colors()

        # Rebuild the current route so controls pick up new `T` colors, then refresh the page
        try:
            self._render_route()
        except Exception:
            pass
        self.page.update()
        self._snack("Settings saved.")

    def _reseed_data(self):
        self._open(dialogs.confirm_dialog(
            "Reset demo data?",
            "This wipes the local SQLite database and re-seeds it with the original sample data.",
            on_confirm=self._do_reseed,
            on_close=self._close_dialog,
            danger=True,
            confirm_label="Reset",
        ))

    def _do_reseed(self):
        db.init_db(force_reseed=True)
        self._close_dialog()
        self.go("/dashboard")
        self._snack("Demo data has been reset.")

    # ---------- public-page helpers ----------
    def _scroll_to_mission(self):
        self._snack("Scroll down to read the mission and impact tiers.")

    # ---------- dialog plumbing ----------
    def _open(self, dlg: ft.Control):
        self._open_dialogs.append(dlg)
        self.page.open(dlg)

    def _close_dialog(self):
        if not self._open_dialogs:
            return
        dlg = self._open_dialogs.pop()
        self.page.close(dlg)

    def _snack(self, msg: str):
        # Use primary color for snack background and ON_PRIMARY for text to ensure contrast
        self.page.open(ft.SnackBar(content=ft.Text(msg, color=T.ON_PRIMARY), bgcolor=T.PRIMARY))


def _kv(label: str, value: str):
    return ft.Row(
        [
            ft.Text(label, size=12, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600, width=140),
            ft.Text(value, size=12, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
        ],
    )


def main(page: ft.Page):
    db.init_db()
    app = App(page)
    initial = page.route or "/dashboard"
    if initial in (None, "", "/"):
        initial = "/dashboard"
    app.go(initial)

    def on_route_change(e):
        target = page.route or "/dashboard"
        if target != getattr(app, "current_route", None):
            app.go(target)
    page.on_route_change = on_route_change


if __name__ == "__main__":
    ft.app(target=main)
