"""Convenience runner for the Charity Transparency Ledger app.

Usage:
    python run.py            # desktop window
    python run.py --web      # in browser
"""
import sys
import flet as ft

from charity_ledger.main import main


if __name__ == "__main__":
    if "--web" in sys.argv:
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
    else:
        ft.app(target=main)
