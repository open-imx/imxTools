from nicegui import ui
from apps.gui.config.ui_constants import MENU_ITEM_STYLE, MENU_CATEGORY_STYLE

def build_drawer():
    def create_button(icon: str, text: str, target: str):
        ui.button(
            text,
            on_click=lambda: ui.navigate.to(target),
            icon=icon
        ).props('flat').classes(
            "hover:scale-105 transition-transform"
        )

    with ui.drawer(side="left").classes("bg-base-200 shadow-md") as menu:
        with ui.column().classes("p-4 gap-3"):

            # Close button
            ui.icon('fa-solid fa-xmark').classes(
                "text-lg cursor-pointer self-end hover:scale-110 transition-transform"
            ).tooltip("Close menu").on('click', lambda: menu.toggle())

            # Report category
            ui.label("📊 Report").classes("text-md font-bold").style(MENU_CATEGORY_STYLE)
            with ui.column().classes("pl-2 gap-1 text-sm"):
                create_button("fa-solid fa-code-compare", "Diff Report", "/diff")
                create_button("fa-solid fa-chart-column", "Population Report", "/population")
                create_button("fa-solid fa-comment-dots", "Comments", "/comments")
                create_button("fa-solid fa-road", "KM Report", "/km-excel")
                create_button("fa-solid fa-ruler-combined", "Measure Check", "/measure")

            # Tools category
            ui.label("🛠️ Tools").classes("text-md font-bold").style(MENU_CATEGORY_STYLE)
            with ui.column().classes("pl-2 gap-1 text-sm"):
                create_button("fa-solid fa-pen-to-square", "Revisions", "/revision")
                create_button("fa-solid fa-wrench", "Measure Correction", "/measure-correction-flow")
                create_button("fa-solid fa-location-crosshairs", "KM Lookup", "/km")

    return menu
