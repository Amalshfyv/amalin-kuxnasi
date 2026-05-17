import flet as ft
from datetime import datetime
import secrets

from .. import db, theme as T
from ..components.shell import brand


def _stepper(active: int):
    def _step(num, label):
        is_active = num == active
        is_done = num < active
        bg = T.PRIMARY if is_active else T.BG_CARD
        fg = T.ON_PRIMARY if is_active else T.TEXT_MUTED
        border = T.PRIMARY if is_active or is_done else T.BORDER
        circle = ft.Container(
            content=ft.Text(str(num) if not is_done else "✓", size=12, weight=ft.FontWeight.W_700, color=fg if not is_done else T.PRIMARY),
            width=32,
            height=32,
            bgcolor=bg,
            border=ft.border.all(1, border),
            border_radius=999,
            alignment=ft.alignment.center,
        )
        return ft.Column(
            [
                circle,
                ft.Container(height=4),
                ft.Text(label, size=11, color=T.PRIMARY if is_active else T.TEXT_MUTED, weight=ft.FontWeight.W_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

    def _connector():
        return ft.Container(width=160, height=1, bgcolor=T.BORDER)

    return ft.Row(
        [
            _step(1, "Selection"),
            _connector(),
            _step(2, "Payment"),
            _connector(),
            _step(3, "Confirmation"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _topbar(on_admin):
    return ft.Container(
        height=64,
        padding=ft.padding.symmetric(horizontal=24, vertical=10),
        bgcolor=T.BG_CARD,
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
                T.outline_button("Admin Login", on_click=on_admin),
            ]
        ),
    )


def _security_strip():
    return ft.Row(
        [
            ft.Row(
                [ft.Icon(ft.Icons.SHIELD_OUTLINED, size=12, color=T.TEXT_MUTED),
                 ft.Text("PCI-DSS COMPLIANT", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700)],
                spacing=4,
            ),
            ft.Container(width=24),
            ft.Row(
                [ft.Icon(ft.Icons.LOCK_OUTLINED, size=12, color=T.TEXT_MUTED),
                 ft.Text("256-BIT ENCRYPTION", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700)],
                spacing=4,
            ),
            ft.Container(width=24),
            ft.Row(
                [ft.Icon(ft.Icons.PUBLIC, size=12, color=T.TEXT_MUTED),
                 ft.Text("GLOBAL AUDIT READY", size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700)],
                spacing=4,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )


def _public_footer():
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        border=ft.border.only(top=ft.BorderSide(1, T.BORDER)),
        bgcolor=T.BG_CARD,
        content=ft.Row(
            [
                ft.Text("© 2024 Charity Transparency Ledger.  System Status: Operational", size=11, color=T.TEXT_MUTED),
                ft.Container(expand=True),
                ft.Text("Privacy Policy", size=11, color=T.TEXT_MUTED),
                ft.Container(width=14),
                ft.Text("Audit Log", size=11, color=T.TEXT_MUTED),
            ],
        ),
    )


class DonateFlow:
    def __init__(self, page: ft.Page, on_admin_login, on_finish):
        self.page = page
        self.on_admin_login = on_admin_login
        self.on_finish = on_finish
        self.step = 1
        self.selected_project = "Clean Water Initiative"
        self.amount = 50.0
        self.donor_name = ""
        self.payment_method = "Stripe / Credit Card"
        self.last_tx = None
        self.amount_field = ft.TextField(
            value=str(int(self.amount)),
            prefix_text="$ ",
            border=ft.InputBorder.OUTLINE,
            border_color=T.BORDER,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=12),
            text_size=14,
            on_change=self._on_amount_change,
        )

    def _on_amount_change(self, e):
        try:
            self.amount = float(self.amount_field.value or 0)
        except ValueError:
            self.amount = 0.0

    def _project_option(self, name, desc, icon, sel):
        return ft.Container(
            on_click=lambda e: self._select_project(name),
            ink=True,
            padding=ft.padding.all(14),
            border=ft.border.all(1, T.PRIMARY if sel else T.BORDER),
            border_radius=10,
            bgcolor=T.PRIMARY_LIGHT if sel else T.BG_CARD,
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=18, color=T.PRIMARY if sel else T.TEXT_SECONDARY),
                        width=36,
                        height=36,
                        bgcolor=T.PRIMARY if sel else T.BG_CARD,
                        border_radius=8,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(name, size=13, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                            ft.Text(desc, size=11, color=T.TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
        )

    def _select_project(self, name):
        self.selected_project = name
        self._render()

    def _amount_pill(self, amt):
        sel = abs(self.amount - amt) < 0.01
        return ft.Container(
            on_click=lambda e: self._set_amount(amt),
            ink=True,
            padding=ft.padding.symmetric(horizontal=10, vertical=10),
            border=ft.border.all(1, T.PRIMARY if sel else T.BORDER),
            border_radius=8,
            bgcolor=T.PRIMARY if sel else T.BG_CARD,
            expand=True,
            content=ft.Text(
                T.fmt_money(amt),
                size=13,
                weight=ft.FontWeight.W_700,
                color=T.ON_PRIMARY if sel else T.TEXT_PRIMARY,
                text_align=ft.TextAlign.CENTER,
            ),
        )

    def _set_amount(self, amt):
        self.amount = amt
        self.amount_field.value = str(int(amt))
        self._render()

    def _payment_method_option(self, label, icon, sel):
        return ft.Container(
            on_click=lambda e: self._set_payment(label),
            ink=True,
            padding=ft.padding.all(14),
            border=ft.border.all(1, T.PRIMARY if sel else T.BORDER),
            border_radius=10,
            bgcolor=T.PRIMARY_LIGHT if sel else T.BG_CARD,
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=T.PRIMARY if sel else T.TEXT_SECONDARY),
                    ft.Text(label, size=13, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                    ft.Container(expand=True),
                    ft.Icon(ft.Icons.CHECK_CIRCLE if sel else ft.Icons.RADIO_BUTTON_UNCHECKED, color=T.PRIMARY if sel else T.TEXT_MUTED, size=16),
                ],
                spacing=10,
            ),
        )

    def _set_payment(self, method):
        self.payment_method = method
        self._render()

    def _step_1(self):
        project_controls = []
        for p in db.list_projects():
            icon = ft.Icons.VOLUNTEER_ACTIVISM_OUTLINED
            cat = p.get("category", "")
            if cat == "Environment":
                icon = ft.Icons.WATER_DROP_OUTLINED if "water" in p["name"].lower() else ft.Icons.PARK_OUTLINED
            elif cat == "Education":
                icon = ft.Icons.SCHOOL_OUTLINED
            elif cat == "Humanitarian":
                icon = ft.Icons.HEALTH_AND_SAFETY_OUTLINED
            
            project_controls.append(
                self._project_option(
                    p["name"], 
                    p.get("description", ""), 
                    icon, 
                    self.selected_project == p["name"]
                )
            )
            project_controls.append(ft.Container(height=10))
            
        return T.card(
            ft.Column(
                [
                    T.section_title("Choose Your Impact", size=18),
                    T.subtitle("Select a project you would like to support today."),
                    ft.Container(height=14),
                ] + project_controls + [
                    ft.Container(height=18),
                    ft.Text("Donation Amount ($)", size=13, weight=ft.FontWeight.W_700),
                    ft.Container(height=8),
                    ft.Row(
                        [
                            self._amount_pill(10),
                            self._amount_pill(25),
                            self._amount_pill(50),
                            self._amount_pill(100),
                            self._amount_pill(250),
                        ],
                        spacing=8,
                    ),
                    ft.Container(height=10),
                    self.amount_field,
                    ft.Container(height=18),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Text("Continue to Payment", size=13, weight=ft.FontWeight.W_700, color=T.ON_PRIMARY),
                                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=T.ON_PRIMARY, size=18),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=4,
                            tight=True,
                        ),
                        height=48,
                        on_click=lambda e: self._goto(2),
                        style=ft.ButtonStyle(
                            bgcolor=T.PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                        ),
                    ),
                ],
                spacing=0,
            ),
            padding=24,
            width=540,
        )

    def _step_2(self):
        name_field = ft.TextField(
            label="Full Name",
            value=self.donor_name,
            border=ft.InputBorder.OUTLINE,
            border_color=T.BORDER,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=12),
            text_size=13,
            on_change=lambda e: setattr(self, "donor_name", e.control.value),
        )
        return T.card(
            ft.Column(
                [
                    T.section_title("Payment Details", size=18),
                    T.subtitle(f"Confirm contribution of {T.fmt_money(self.amount)} to {self.selected_project}."),
                    ft.Container(height=14),
                    name_field,
                    ft.Container(height=14),
                    ft.Text("Payment Method", size=13, weight=ft.FontWeight.W_700),
                    ft.Container(height=8),
                    self._payment_method_option("Stripe / Credit Card", ft.Icons.CREDIT_CARD, self.payment_method == "Stripe / Credit Card"),
                    ft.Container(height=8),
                    self._payment_method_option("PayPal", ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, self.payment_method == "PayPal"),
                    ft.Container(height=8),
                    self._payment_method_option("Wire Transfer", ft.Icons.ACCOUNT_BALANCE_OUTLINED, self.payment_method == "Wire Transfer"),
                    ft.Container(height=18),
                    ft.Row(
                        [
                            T.outline_button("Back", on_click=lambda e: self._goto(1), expand=True),
                            ft.Container(width=10),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Text("Confirm & Pay", size=13, weight=ft.FontWeight.W_700, color=T.ON_PRIMARY),
                                            ft.Icon(ft.Icons.LOCK_OUTLINED, color=T.ON_PRIMARY, size=14),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=4,
                                    tight=True,
                                ),
                                height=48,
                                expand=True,
                                on_click=lambda e: self._submit(),
                                style=ft.ButtonStyle(
                                    bgcolor=T.PRIMARY,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    elevation=0,
                                ),
                            ),
                        ],
                    ),
                ],
                spacing=0,
            ),
            padding=24,
            width=540,
        )

    def _submit(self):
        tx_id = f"TX-{secrets.token_hex(3).upper()}"
        h = "0x" + secrets.token_hex(3) + "..." + secrets.token_hex(2)
        donor = self.donor_name.strip() or "Anonymous"
        tx = {
            "id": tx_id,
            "donor": donor,
            "project": self.selected_project,
            "date": datetime.now().strftime("%b %d, %Y"),
            "amount": float(self.amount or 0),
            "status": "Verified",
            "payment_method": self.payment_method,
            "blockchain_hash": h,
            "gateway_response": '{"code": 200, "message": "Authorized", "auth_code": "AUTH_NEW"}',
        }
        try:
            db.insert_transaction(tx)
        except Exception:
            pass
        self.last_tx = tx
        self._goto(3)

    def _step_3(self):
        tx = self.last_tx or {}
        return T.card(
            ft.Column(
                [
                    ft.Container(
                        width=64,
                        height=64,
                        bgcolor=T.SUCCESS_BG,
                        border_radius=999,
                        alignment=ft.alignment.center,
                        content=ft.Icon(ft.Icons.CHECK_ROUNDED, size=34, color=T.SUCCESS),
                    ),
                    ft.Container(height=14),
                    T.section_title("Donation Confirmed", size=20),
                    ft.Container(height=4),
                    T.subtitle("Your contribution has been recorded on the public ledger."),
                    ft.Container(height=18),
                    ft.Container(
                        padding=ft.padding.all(16),
                        border=ft.border.all(1, T.BORDER),
                        border_radius=8,
                        content=ft.Column(
                            [
                                _kv("Reference", tx.get("id", "—")),
                                _kv("Project", tx.get("project", "—")),
                                _kv("Amount", T.fmt_money(tx.get("amount", 0), 2)),
                                _kv("Status", tx.get("status", "—")),
                                _kv("Verification", tx.get("blockchain_hash", "—"), color=T.PRIMARY),
                            ],
                            spacing=8,
                        ),
                    ),
                    ft.Container(height=18),
                    ft.Row(
                        [
                            T.outline_button("Make Another Donation", on_click=lambda e: self._reset(), expand=True),
                            ft.Container(width=10),
                            T.primary_button("Done", on_click=lambda e: self.on_finish(), expand=True),
                        ]
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=28,
            width=540,
        )

    def _reset(self):
        self.step = 1
        self.donor_name = ""
        self.last_tx = None
        self._render()

    def _goto(self, step):
        self.step = step
        self._render()

    def _body(self):
        if self.step == 1:
            content = self._step_1()
        elif self.step == 2:
            content = self._step_2()
        else:
            content = self._step_3()
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=24, vertical=30),
            bgcolor=T.BG_APP,
            content=ft.Column(
                [
                    _stepper(self.step),
                    ft.Container(height=24),
                    ft.Row([ft.Container(expand=True), content, ft.Container(expand=True)]),
                    ft.Container(height=18),
                    _security_strip(),
                ],
                spacing=0,
            ),
            expand=True,
        )

    def render(self):
        self.root = ft.Column(
            [
                _topbar(self.on_admin_login),
                self._body(),
                _public_footer(),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        return self.root

    def _render(self):
        new = ft.Column(
            [
                _topbar(self.on_admin_login),
                self._body(),
                _public_footer(),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.root.controls = new.controls
        self.page.update()


def _kv(label, value, color=None):
    if color is None:
        color = T.TEXT_PRIMARY
    return ft.Row(
        [
            ft.Text(label, size=12, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600),
            ft.Container(expand=True),
            ft.Text(value, size=12, weight=ft.FontWeight.W_700, color=color),
        ],
    )
