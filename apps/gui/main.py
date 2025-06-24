from nicegui import ui

from apps.gui.pages.diff_page import DiffPage
from apps.gui.pages.measure_page import MeasurePage
from apps.gui.pages.population_page import PopulationPage
from apps.gui.pages.revision_page import RevisionPage


# -- Layout used by all pages --
def layout():
    with ui.header().classes("bg-base-200 text-base-content"):
        ui.button(on_click=lambda: menu.toggle()).props("flat dense icon=menu").classes(
            "ml-2"
        )
        ui.label("IMX Insights").classes("text-xl font-bold ml-4")
        with ui.row().classes("ml-auto mr-4"):
            pass  # No dark mode switch here anymore

    with ui.drawer(side="left") as menu:
        with ui.column().classes("p-4"):
            ui.link("🏠 Home", target="/")
            ui.link("🧮 Diff Tool", target="/diff")
            ui.link("📊 Population Tool", target="/population")
            ui.link("📐 Measure Check", target="/measure")
            ui.link("📝 Apply Revisions", target="/revision")


# -- Pages --
@ui.page("/")
def home_page():
    layout()
    ui.label("Welcome to IMX Insights").classes("text-2xl p-4")


@ui.page("/diff")
def diff_page():
    layout()
    DiffPage()


@ui.page("/population")
def population_page():
    layout()
    PopulationPage()


@ui.page("/measure")
def measure_page():
    layout()
    MeasurePage()


@ui.page("/revision")
def revision_page():
    layout()
    RevisionPage()


# -- Run the app --
ui.run(title="IMX Insights", reload=False)
