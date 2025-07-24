import sys
from nicegui import ui, native, app

from apps.gui.components.layouts.layout import create_layout
from apps.gui.components.widgets.version_check_dialog import version_stage_warning, new_version_release_dialog
from apps.gui.pages.add_km_excel_page import AddKmExcelPage
from apps.gui.pages.comment_page import CommentPage
from apps.gui.pages.diff_page import DiffPage
from apps.gui.pages.km_page import KmPage
from apps.gui.pages.measure_correction_flow_page import MeasureCorrectionFlowPage
from apps.gui.pages.measure_page import MeasurePage
from apps.gui.pages.population_page import PopulationPage
from apps.gui.pages.revision_page import RevisionPage
from src.imxTools import __version__ as build_version


@ui.page("/")
async def home_page():
    dark_mode = ui.dark_mode()
    saved_state = app.storage.user.get('dark_mode', True)
    dark_mode.enable() if saved_state else dark_mode.disable()

    await create_layout()
    await version_stage_warning()
    await new_version_release_dialog()
    with ui.column().classes("w-full items-center justify-center"):
        ui.label("Welcome to IMX Tools").classes("text-2xl p-4")
        ui.label(f"v{build_version}").classes("text-4xl p-4")


@ui.page("/diff")
async def diff_page():
    await create_layout()
    DiffPage()


@ui.page("/population")
async def population_page():
    await create_layout()
    PopulationPage()


@ui.page("/comments")
async def comments_page():
    await create_layout()
    CommentPage()


@ui.page("/revision")
async def revision_page():
    await create_layout()
    RevisionPage()


@ui.page("/km")
async def km_page():
    await create_layout()
    KmPage()


@ui.page("/km-excel")
async def km_excel_page():
    await create_layout()
    AddKmExcelPage()


@ui.page("/measure")
async def measure_page():
    await create_layout()
    MeasurePage()


@ui.page("/measure-correction-flow")
async def measure_correction_flow_page():
    await create_layout()
    MeasureCorrectionFlowPage()


if __name__ == "__main__":
    is_frozen = getattr(sys, "frozen", False)
    chosen_port = 8003 if is_frozen else native.find_open_port()
    ui.run(
        reload=False,
        port=chosen_port,
        title="IMX 🛠️ Tools",
        fastapi_docs=True,
        storage_secret="super-secret-key",  # REQUIRED for app.storage.user
    )