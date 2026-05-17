import flet as ft
from .. import theme as T
from ..components.shell import brand

def view(page: ft.Page, on_login_success, on_back):
    # Fetch saved credentials
    saved_email = page.client_storage.get("admin_email") or ""
    saved_password = page.client_storage.get("admin_password") or ""
    remember_me_val = bool(saved_email and saved_password)

    email_field = ft.TextField(
        label="Email Address",
        value=saved_email,
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        keyboard_type=ft.KeyboardType.EMAIL,
        border_color=T.BORDER,
        focused_border_color=T.PRIMARY,
        text_size=14,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=16),
        autofocus=not saved_email,
        border_radius=8,
    )
    
    password_field = ft.TextField(
        label="Password",
        value=saved_password,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_color=T.BORDER,
        focused_border_color=T.PRIMARY,
        text_size=14,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=16),
        border_radius=8,
        autofocus=bool(saved_email and not saved_password),
    )
    
    remember_checkbox = ft.Checkbox(
        label="Remember Me", 
        value=remember_me_val, 
        fill_color=T.PRIMARY
    )
    
    error_text = ft.Text("", color=T.DANGER, size=13, weight=ft.FontWeight.W_600, visible=False)

    def on_login_click(e):
        if email_field.value == "amalshafiyev07@gmail.com" and password_field.value == "amal1234":
            error_text.visible = False
            email_field.update()
            password_field.update()
            error_text.update()
            
            # Save or clear credentials
            if remember_checkbox.value:
                page.client_storage.set("admin_email", email_field.value)
                page.client_storage.set("admin_password", password_field.value)
            else:
                page.client_storage.remove("admin_email")
                page.client_storage.remove("admin_password")
                
            on_login_success()
        else:
            error_text.value = "Invalid email or password"
            error_text.visible = True
            error_text.update()

    # Create a nice layout
    form_container = ft.Container(
        width=420,
        padding=ft.padding.all(40),
        bgcolor=T.BG_CARD,
        border_radius=16,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=30,
            color=T.TEXT_PRIMARY,
            offset=ft.Offset(0, 10),
        ),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: on_back(), icon_color=T.TEXT_SECONDARY, tooltip="Go Back"),
                        ft.Container(expand=True),
                        brand(size=18),
                        ft.Container(width=40), # Balance the back button
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=24),
                ft.Column(
                    [
                        ft.Text("Welcome Back", size=28, weight=ft.FontWeight.W_800, color=T.TEXT_PRIMARY),
                        ft.Text("Please enter your credentials to access the admin panel", size=14, color=T.TEXT_SECONDARY),
                    ],
                    spacing=4,
                ),
                ft.Container(height=32),
                email_field,
                ft.Container(height=16),
                password_field,
                ft.Container(height=8),
                ft.Row([remember_checkbox], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=8),
                error_text,
                ft.Container(height=24),
                ft.ElevatedButton(
                    text="Login",
                    on_click=on_login_click,
                    height=48,
                    style=ft.ButtonStyle(
                        bgcolor=T.PRIMARY,
                        color=T.ON_PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        elevation=2,
                        text_style=ft.TextStyle(weight=ft.FontWeight.W_700, size=15),
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=0,
        ),
    )

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[T.PRIMARY_CONTAINER, T.PRIMARY],
        ),
        alignment=ft.alignment.center,
        content=form_container,
    )
