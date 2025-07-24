import importlib.metadata
import sys

from nicegui import ui, native

from apps.gui.components.flashbang_toggle import create_dark_mode_toggle
from apps.gui.components.widgets.versionCheckDialog import version_stage_warning, new_version_release_dialog
from apps.gui.pages.add_km_excel_page import AddKmExcelPage
from apps.gui.pages.comment_page import CommentPage
from apps.gui.pages.diff_page import DiffPage
from apps.gui.pages.km_page import KmPage
from apps.gui.pages.measure_correction_flow_page import MeasureCorrectionFlowPage
from apps.gui.pages.measure_page import MeasurePage
from apps.gui.pages.population_page import PopulationPage
from apps.gui.pages.revision_page import RevisionPage

from src.imxTools import __version__ as imx_tools_version
from src.imxTools import __version__ as build_version


async def layout():
    menu_item_style = 'color: #6E93D6; font-size: 150%; font-weight: 300; padding:5px'
    menu_category_style = 'color: white; font-size: 150%; font-weight: 300; padding:5px'

    with ui.header().classes("bg-base-200 text-base-content shadow-md"):
        with ui.row().classes("w-full items-center justify-between"):

            with ui.row().classes("items-center gap-2 ml-2"):
                ui.button(on_click=lambda: menu.toggle()).props(
                    "flat dense icon=menu"
                ).classes("text-lg black text-black")
                ui.label("IMX Tools").classes("text-2xl font-bold cursor-pointer text-white").on("click", lambda: ui.navigate.to("/"))

            with ui.row().classes("items-center mr-4 gap-2"):
                await version_stage_warning()
                await new_version_release_dialog(as_button=True)
                # here can we add dark light and profile icons.
                create_dark_mode_toggle()

    with ui.drawer(side="left").classes("bg-base-200 shadow-md") as menu:
        with ui.column().classes("p-4 gap-2"):
            ui.label("📊 Report").classes("text-md font-bold text-gray-600").style(menu_category_style)
            with ui.column().classes("pl-2 gap-1 text-sm"):
                ui.link("🧮 Diff Report", target="/diff").style(menu_item_style)
                ui.link("📊 Population Report", target="/population").style(menu_item_style)
                ui.link("💬 Comments", target="/comments").style(menu_item_style)
                ui.link("📍 KM Report", target="/km-excel").style(menu_item_style)
                ui.link("📐 Measure Check", target="/measure").style(menu_item_style)

            ui.label("🛠️ Tools").classes("text-md font-bold text-gray-600").style(menu_category_style)
            with ui.column().classes("pl-2 gap-1 text-sm"):
                ui.link("📝 Revisions", target="/revision").style(menu_item_style)
                ui.link("🔧 Measure Correction", target="/measure-correction-flow").style(menu_item_style)
                ui.link("📍 KM Lookup", target="/km").style(menu_item_style)


    with ui.footer().style("background-color: #3874c8"):
        with ui.column().classes("gap-0 p-0"):
            ui.label(f"ImxTools v{imx_tools_version}").classes("text-lg m-0").style(
                "line-height: 1"
            )
            ui.label(
                f"using ImxInsights v{importlib.metadata.version('imxInsights')}"
            ).classes("text-xs mt-1").style("line-height: 1")


@ui.page("/")
async def home_page():  # noqa: F811
    await version_stage_warning()
    await new_version_release_dialog()
    await layout()

    with ui.column().classes("w-full items-center justify-center"):
        ui.label("Welcome to IMX Tools").classes("text-2xl p-4")
        ui.label(f"v{build_version}").classes("text-4xl p-4")

@ui.page("/diff")
async def diff_page():  # noqa: F811
    await layout()
    DiffPage()


@ui.page("/population")
async def population_page():  # noqa: F811
    await layout()
    PopulationPage()


@ui.page("/comments")
async def revision_page():  # noqa: F811
    await layout()
    CommentPage()


@ui.page("/revision")
async def revision_page():  # noqa: F811
    await layout()
    RevisionPage()


@ui.page("/km")
async def km_page():  # noqa: F811
    await layout()
    KmPage()


@ui.page("/km-excel")
async def km_page():  # noqa: F811
    await layout()
    AddKmExcelPage()


@ui.page("/measure")
async def measure_page():  # noqa: F811
    await layout()
    MeasurePage()


@ui.page("/measure-correction-flow")
async def km_page():  # noqa: F811
    await layout()
    MeasureCorrectionFlowPage()


if __name__ == "__main__":
    is_frozen = getattr(sys, "frozen", False)
    chosen_port = 8003 if is_frozen else native.find_open_port()

    ui.run(
        reload=False,
        port=chosen_port,
        title="IMX 🛠️ Tools",
        dark=True,
        fastapi_docs=True,
    )

