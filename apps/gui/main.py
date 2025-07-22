import importlib.metadata

from nicegui import ui

from apps.gui.components.widgets.versionCheckDialog import version_stage_warning, new_version_release_dialog
from apps.gui.pages.add_km_excel_page import AddKmExcelPage
# from apps.gui.pages.comment_page import CommentPage
from apps.gui.pages.diff_page import DiffPage
from apps.gui.pages.km_page import KmPage
from apps.gui.pages.measure_correction_flow_page import MeasureCorrectionFlowPage
from apps.gui.pages.measure_page import MeasurePage
from apps.gui.pages.population_page import PopulationPage
from apps.gui.pages.revision_page import RevisionPage

from src.imxTools import __version__ as imx_tools_version
from src.imxTools import __version__ as build_version


async def layout():
    with ui.header().classes("bg-base-200 text-base-content shadow-md"):
        with ui.row().classes("w-full items-center justify-between"):

            with ui.row().classes("items-center gap-2 ml-2"):
                ui.button("🛠️", on_click=lambda: menu.toggle()).props(
                    "flat dense icon=menu"
                ).classes("text-lg")
                ui.label("IMX Tools").classes("text-2xl font-bold")

            with ui.row().classes("items-center mr-4 gap-2"):
                await version_stage_warning()
                await new_version_release_dialog(as_button=True)
                # here can we add dark light and profile icons.


    with ui.drawer(side="left") as menu:
        with ui.column().classes("p-4"):
            ui.link("🏠 Home", target="/")
            ui.separator()
            ui.label("🛠️ Tools")
            with ui.column().classes("pl-4"):
                ui.link("🧮 Diff Report", target="/diff")
                ui.link("📊 Population Report", target="/population")
                # ui.link("💬 Comments", target="/comments")
                ui.link("📝 Revisions", target="/revision")
                ui.link("📐 Measure Check", target="/measure")
                ui.link("🔧 Measure Correction", target="/measure-correction-flow")
                ui.link("📍 KM Report", target="/km-excel")
                ui.link("📍 KM Lookup", target="/km")

    with ui.footer().style("background-color: #3874c8"):
        with ui.column().classes("gap-0 p-0"):
            ui.label(f"ImxTools v{imx_tools_version}").classes("text-lg m-0").style(
                "line-height: 1"
            )
            ui.label(
                f"using ImxInsights v{importlib.metadata.version('imxInsights')}"
            ).classes("text-xs mt-1").style("line-height: 1")
        # await new_version_release_dialog(as_button=True)


@ui.page("/")
async def home_page():  # noqa: F811
    await version_stage_warning()
    await new_version_release_dialog()
    await layout()

    ui.label("Welcome to IMX Tools").classes("text-2xl p-4")


    ui.add_body_html(
        '<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>'
    )

    src = "https://lottie.host/838bfce2-f68e-4cd4-a14a-fe2ae95b7e2f/gfeOVDiswh.json"
    ui.html(f'<lottie-player src="{src}" loop autoplay />').classes("w-full")

    with ui.column().classes("w-full items-center justify-center"):
        ui.label(f"v{build_version}: Texas Twinkies").classes("text-4xl p-4")

@ui.page("/diff")
async def diff_page():  # noqa: F811
    await layout()
    DiffPage()


@ui.page("/population")
async def population_page():  # noqa: F811
    await layout()
    PopulationPage()


# @ui.page("/comments")
# async def revision_page():  # noqa: F811
#     await layout()
#     CommentPage()


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


ui.run(title="IMX 🛠️ Tools", reload=False)
