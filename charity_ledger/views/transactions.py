import flet as ft

from .. import db, theme as T


STATUS_OPTIONS = ["All", "Verified", "Pending", "Failed"]


def _row(t, on_action):
    return ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(t["id"], size=12, color=T.PRIMARY, weight=ft.FontWeight.W_600)),
            ft.DataCell(ft.Text(t["donor"], size=12, color=T.TEXT_PRIMARY)),
            ft.DataCell(ft.Text(t["project"], size=12, color=T.TEXT_SECONDARY)),
            ft.DataCell(ft.Text(t["date"], size=12, color=T.TEXT_SECONDARY)),
            ft.DataCell(ft.Text(T.fmt_money(t["amount"]), size=12, color=T.TEXT_PRIMARY, weight=ft.FontWeight.W_700)),
            ft.DataCell(T.status_pill(t["status"])),
            ft.DataCell(
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_NEW,
                            icon_size=14,
                            icon_color=T.PRIMARY,
                            tooltip="View audit details",
                            on_click=lambda e, tx=t: on_action(tx["id"], "audit"),
                        ),
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            icon_size=16,
                            tooltip="More actions",
                            items=[
                                ft.PopupMenuItem(text="Audit details", icon=ft.Icons.OPEN_IN_NEW,
                                                 on_click=lambda e, tx=t: on_action(tx["id"], "audit")),
                                ft.PopupMenuItem(),
                                ft.PopupMenuItem(text="Mark Verified", icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                                                 on_click=lambda e, tx=t: on_action(tx["id"], "verify")),
                                ft.PopupMenuItem(text="Mark Failed", icon=ft.Icons.ERROR_OUTLINE,
                                                 on_click=lambda e, tx=t: on_action(tx["id"], "fail")),
                                ft.PopupMenuItem(),
                                ft.PopupMenuItem(text="Export CSV", icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
                                                 on_click=lambda e, tx=t: on_action(tx["id"], "export")),
                                ft.PopupMenuItem(text="Delete", icon=ft.Icons.DELETE_OUTLINE,
                                                 on_click=lambda e, tx=t: on_action(tx["id"], "delete")),
                            ],
                        ),
                    ],
                    spacing=0,
                )
            ),
        ]
    )


def _filter(rows, search, status):
    s = (search or "").strip().lower()
    out = list(rows)
    if status and status != "All":
        out = [t for t in out if t["status"] == status]
    if s:
        out = [t for t in out if s in (t["id"] or "").lower()
               or s in (t["donor"] or "").lower()
               or s in (t["project"] or "").lower()]
    return out


def view(on_audit, search_value, status_filter, on_search, on_status_filter,
         on_export, on_audit_ledger, on_tx_action):
    txs = _filter(db.list_transactions(), search_value, status_filter)

    headers = [
        ft.DataColumn(ft.Text("TX ID", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Donor", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Project", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Date", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Amount", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Status", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
        ft.DataColumn(ft.Text("Actions", size=11, color=T.TEXT_MUTED, weight=ft.FontWeight.W_600)),
    ]
    rows = [_row(t, on_tx_action) for t in txs]
    table = ft.DataTable(
        columns=headers,
        rows=rows,
        heading_row_height=36,
        data_row_min_height=48,
        data_row_max_height=52,
        column_spacing=24,
        divider_thickness=0,
        horizontal_margin=4,
    )

    search_field = ft.TextField(
        value=search_value or "",
        hint_text="Search by TX ID, donor or project",
        prefix_icon=ft.Icons.SEARCH,
        border=ft.InputBorder.OUTLINE,
        border_color=T.BORDER,
        border_radius=8,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=10),
        height=40,
        width=280,
        on_submit=lambda e: on_search(e.control.value),
    )
    status_dd = ft.Dropdown(
        value=status_filter or "All",
        options=[ft.dropdown.Option(s) for s in STATUS_OPTIONS],
        border_color=T.BORDER, border_radius=8, text_size=13,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        width=140,
        on_change=lambda e: on_status_filter(e.control.value),
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Column(
                        [
                            T.section_title("Transactions", size=24),
                            T.subtitle("Every contribution recorded on the verified ledger."),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    T.outline_button("Export CSV", icon=ft.Icons.FILE_DOWNLOAD_OUTLINED, on_click=on_export),
                    ft.Container(width=8),
                    T.primary_button("Audit Ledger", icon=ft.Icons.OPEN_IN_NEW, on_click=on_audit_ledger),
                ],
            ),
            ft.Container(height=18),
            T.card(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        T.section_title("Recent Verified Donations", size=16),
                                        T.subtitle(f"{len(txs)} entries"),
                                    ],
                                    spacing=2, expand=True,
                                ),
                                search_field,
                                ft.Container(width=10),
                                status_dd,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=12),
                        ft.Row([table], scroll=ft.ScrollMode.AUTO) if rows else
                        ft.Container(padding=ft.padding.all(28),
                                     content=ft.Text("No transactions match the current filters.", color=T.TEXT_MUTED, size=12),
                                     alignment=ft.alignment.center),
                    ],
                    spacing=0,
                ),
                padding=20,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def audit_dialog(tx, on_close, on_export_csv):
    code_block = ft.Container(
        bgcolor="#0F172A",
        padding=ft.padding.all(14),
        border_radius=8,
        content=ft.Text(
            tx.get("gateway_response") or "{}",
            size=12,
            color="#A5F3FC",
            font_family="Courier",
            selectable=True,
        ),
    )

    def _field(label, value, value_color=None, weight=ft.FontWeight.W_700):
        if value_color is None:
            value_color = T.TEXT_PRIMARY
        return ft.Container(
            padding=ft.padding.all(12),
            border=ft.border.all(1, T.BORDER),
            border_radius=8,
            expand=True,
            content=ft.Column(
                [
                    ft.Text(label.upper(), size=10, color=T.TEXT_MUTED, weight=ft.FontWeight.W_700),
                    ft.Container(height=4),
                    ft.Text(value, size=13, color=value_color, weight=weight),
                ],
                spacing=0,
            ),
        )

    body = ft.Container(
        width=720,
        padding=ft.padding.all(24),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.SHIELD_OUTLINED, size=18, color=T.PRIMARY),
                            width=36, height=36,
                            bgcolor=T.PRIMARY_LIGHT,
                            border_radius=8,
                            alignment=ft.alignment.center,
                        ),
                        ft.Column(
                            [
                                ft.Text("Transaction Audit Details", size=18, weight=ft.FontWeight.W_700),
                                ft.Text(f"Full ledger entry for reference {tx['id']}", size=12, color=T.TEXT_MUTED),
                            ],
                            spacing=2, expand=True,
                        ),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=18, on_click=lambda e: on_close()),
                    ],
                ),
                ft.Container(height=18),
                ft.Row([_field("Transaction ID", tx["id"]), ft.Container(width=12), _field("Processing Date", tx["date"])]),
                ft.Container(height=12),
                ft.Row([_field("Donor Identity", tx["donor"]), ft.Container(width=12), _field("Allocated Project", tx["project"])]),
                ft.Container(height=12),
                ft.Row([_field("Amount (USD)", T.fmt_money(tx["amount"], 2)), ft.Container(width=12), _field("Payment Method", tx["payment_method"] or "—")]),
                ft.Container(height=12),
                _field("Blockchain Verification Hash", tx["blockchain_hash"] or "—", value_color=T.PRIMARY),
                ft.Container(height=18),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.RECEIPT_LONG, size=14, color=T.TEXT_SECONDARY),
                        ft.Text("Payment Gateway Response", size=13, weight=ft.FontWeight.W_700),
                    ],
                    spacing=6,
                ),
                ft.Container(height=8),
                code_block,
                ft.Container(height=18),
                T.divider(),
                ft.Container(height=12),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.SUCCESS, size=14),
                        ft.Text(f"Verified at {tx['date']}", size=12, color=T.TEXT_SECONDARY),
                        ft.Container(expand=True),
                        T.outline_button("Close Ledger", on_click=lambda e: on_close()),
                        ft.Container(width=8),
                        T.primary_button("Export CSV", icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
                                         on_click=lambda e: on_export_csv(tx["id"])),
                    ],
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
    return ft.AlertDialog(
        modal=True,
        content=body,
        content_padding=0,
        bgcolor=T.BG_CARD,
        shape=ft.RoundedRectangleBorder(radius=14),
    )
