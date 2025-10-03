import flet as ft

from layout import LayoutControl


def main(page: ft.Page):
  # config ------------------------------
  page.title = "Yolo App"
  page.theme_mode = ft.ThemeMode.LIGHT
  
  # view ------------------------------
  page.add(
    ft.SafeArea(
      LayoutControl(page)
    )
  )


ft.app(main)
