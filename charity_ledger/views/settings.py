import flet as ft

from .. import theme as T


def view(settings, on_save, on_reseed):
    theme_dd = ft.Dropdown(
        label="Appearance",
        value=settings.get("theme", "Light"),
        options=[ft.dropdown.Option("Light"), ft.dropdown.Option("Dark"), ft.dropdown.Option("System")],
        border_color=T.BORDER, border_radius=8, text_size=13,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
    )
    email_sw = ft.Switch(value=settings.get("notifications_email", True), active_color=T.PRIMARY)
    push_sw = ft.Switch(value=settings.get("notifications_push", False), active_color=T.PRIMARY)
    auto_sw = ft.Switch(value=settings.get("auto_verify", True), active_color=T.PRIMARY)

    def _save(e):
        on_save({
            "theme": theme_dd.value,
            "notifications_email": email_sw.value,
            "notifications_push": push_sw.value,
            "auto_verify": auto_sw.value,
        })

    def _row(label, sub, control):
        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(label, size=13, weight=ft.FontWeight.W_700, color=T.TEXT_PRIMARY),
                        ft.Text(sub, size=11, color=T.TEXT_MUTED),
                    ],
                    spacing=2, expand=True,
                ),
                control,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    appearance_card = T.card(
        ft.Column(
            [
                T.section_title("Appearance", size=16),
                T.subtitle("Match the interface to your preference."),
                ft.Container(height=12),
                theme_dd,
            ],
            spacing=0,
        ),
        padding=20,
    )

    notif_card = T.card(
        ft.Column(
            [
                T.section_title("Notifications", size=16),
                T.subtitle("Choose how you want to be alerted about ledger activity."),
                ft.Container(height=12),
                _row("Email digests", "Daily summary of new donations and pending verifications.", email_sw),
                ft.Container(height=10),
                T.divider(),
                ft.Container(height=10),
                _row("Push notifications", "Instant alerts for high-priority events (failed payments, big gifts).", push_sw),
                ft.Container(height=10),
                T.divider(),
                ft.Container(height=10),
                _row("Auto-verify low-risk transactions", "Automatically mark verified-by-gateway transactions as audited.", auto_sw),
            ],
            spacing=0,
        ),
        padding=20,
    )

    danger_card = T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING_AMBER, size=18, color=T.DANGER),
                        T.section_title("Demo Data", size=16),
                    ],
                    spacing=8,
                ),
                T.subtitle("Reset the local SQLite database back to the original sample contents."),
                ft.Container(height=12),
                ft.ElevatedButton(
                    "Reset demo data",
                    icon=ft.Icons.RESTART_ALT,
                    on_click=lambda e: on_reseed(),
                    style=ft.ButtonStyle(
                        bgcolor=T.DANGER, color=ft.colors.ON_PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        elevation=0,
                        padding=ft.padding.symmetric(horizontal=18, vertical=10),
                        text_style=ft.TextStyle(weight=ft.FontWeight.W_600, size=13),
                    ),
                ),
            ],
            spacing=4,
        ),
        padding=20,
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            T.section_title("Settings", size=24),
                            T.subtitle("Tune appearance, notification preferences, and demo data."),
                        ],
                        spacing=4, expand=True,
                    ),
                    T.primary_button("Save Changes", icon=ft.Icons.SAVE, on_click=_save),
                ],
            ),
            ft.Container(height=18),
            appearance_card,
            ft.Container(height=14),
            notif_card,
            ft.Container(height=14),
            danger_card,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
