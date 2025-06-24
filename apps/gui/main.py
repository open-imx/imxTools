from nicegui import ui

from apps.gui.pages.diff_page import DiffPage
from apps.gui.pages.km_page import KmPage
from apps.gui.pages.measure_page import MeasurePage
from apps.gui.pages.population_page import PopulationPage
from apps.gui.pages.revision_page import RevisionPage


# -- Layout used by all pages --
def layout():
    with ui.header().classes("bg-base-200 text-base-content"):
        ui.button(on_click=lambda: menu.toggle()).props("flat dense icon=menu").classes(
            "ml-2"
        )
        ui.label("IMX Tools").classes("text-xl font-bold ml-4")
        with ui.row().classes("ml-auto mr-4"):
            pass  # No dark mode switch here anymore

    with ui.drawer(side="left") as menu:
        with ui.column().classes("p-4"):
            ui.link("🏠 Home", target="/")
            ui.separator()

            ui.label('🔄 Work Flows')
            with ui.column().classes("pl-4"):
                ui.link("🔧 Measure Correction", target="/")
                ui.link("➕ Add km to report", target="/")

            ui.separator()

            ui.label('🛠️ Tools')
            with ui.column().classes("pl-4"):
                ui.link("🧮 Diff Report", target="/diff")
                ui.link("📊 Population Report", target="/population")
                ui.link("📐 Measure Check", target="/measure")
                ui.link("📝 Revisions", target="/revision")
                ui.link("📍 KM Lookup", target="/km")


# -- Pages --
@ui.page("/")
def home_page():
    layout()
    ui.label("Welcome to IMX Tools").classes("text-2xl p-4")


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

@ui.page("/km")
def km_page():
    layout()
    KmPage()


# -- Run the app --
ui.run(title="IMX Insights", reload=False)
