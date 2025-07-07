import importlib.metadata

from nicegui import ui

from apps.gui.pages.add_km_excel_page import AddKmExcelPage
from apps.gui.pages.comment_page import CommentPage
from apps.gui.pages.diff_page import DiffPage
from apps.gui.pages.km_page import KmPage
from apps.gui.pages.measure_correction_flow_page import MeasureCorrectionFlowPage
from apps.gui.pages.measure_page import MeasurePage
from apps.gui.pages.population_page import PopulationPage
from apps.gui.pages.revision_page import RevisionPage

from src.imxTools import __version__ as imx_tools_version

def layout():
    with ui.header().classes("bg-base-200 text-base-content"):
        ui.button("🛠️", on_click=lambda: menu.toggle()).props("flat dense icon=menu").classes(
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
                ui.link("🔧 Measure Correction", target="/measure-correction-flow")
                ui.link("➕ Add km to report", target="/")

            ui.separator()

            ui.label('🛠️ Tools')
            with ui.column().classes("pl-4"):
                ui.link("🧮 Diff Report", target="/diff")
                ui.link("📊 Population Report", target="/population")
                ui.link("💬 Comments", target="/comments")
                ui.link("📝 Revisions", target="/revision")
                ui.link("📍 KM Lookup", target="/km")
                ui.link("📐 Measure Check", target="/measure")

    with ui.footer().style('background-color: #3874c8'):
        with ui.column().classes('gap-0 p-0'):
            ui.label(f"ImxTools v{imx_tools_version}").classes('text-lg m-0').style('line-height: 1')
            ui.label(f"using ImxInsights v{importlib.metadata.version('imxInsights')}").classes('text-xs mt-1').style('line-height: 1')


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


@ui.page("/comments")
def revision_page():
    layout()
    CommentPage()

@ui.page("/revision")
def revision_page():
    layout()
    RevisionPage()


@ui.page("/km")
def km_page():
    layout()
    KmPage()

@ui.page("/km-excel")
def km_page():
    layout()
    AddKmExcelPage()




@ui.page("/measure")
def measure_page():
    layout()
    MeasurePage()


@ui.page("/measure-correction-flow")
def km_page():
    layout()
    MeasureCorrectionFlowPage()


ui.run(title="IMX 🛠️ Tijn Tool", reload=False)
