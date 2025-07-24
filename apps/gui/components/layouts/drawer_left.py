from nicegui import ui
from apps.gui.config.ui_constants import MENU_ITEM_STYLE, MENU_CATEGORY_STYLE

def build_drawer():
    with ui.drawer(side="left").classes("bg-base-200 shadow-md") as menu:
        with ui.column().classes("p-4 gap-2"):
            ui.label("📊 Report").classes("text-md font-bold text-gray-600").style(MENU_CATEGORY_STYLE)
            with ui.column().classes("pl-2 gap-1 text-sm"):
                ui.link("🧮 Diff Report", target="/diff").style(MENU_ITEM_STYLE)
                ui.link("📊 Population Report", target="/population").style(MENU_ITEM_STYLE)
                ui.link("💬 Comments", target="/comments").style(MENU_ITEM_STYLE)
                ui.link("📍 KM Report", target="/km-excel").style(MENU_ITEM_STYLE)
                ui.link("📐 Measure Check", target="/measure").style(MENU_ITEM_STYLE)

            ui.label("🛠️ Tools").classes("text-md font-bold text-gray-600").style(MENU_CATEGORY_STYLE)
            with ui.column().classes("pl-2 gap-1 text-sm"):
                ui.link("📝 Revisions", target="/revision").style(MENU_ITEM_STYLE)
                ui.link("🔧 Measure Correction", target="/measure-correction-flow").style(MENU_ITEM_STYLE)
                ui.link("📍 KM Lookup", target="/km").style(MENU_ITEM_STYLE)
    return menu
