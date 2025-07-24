from nicegui import ui
from nicegui.element import Element

from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp
from apps.gui.components.tools.kmExcelTool import KmExcelTool
from apps.gui.helpers.io import load_markdown
from apps.gui.helpers.km_service_manager import is_km_service_running, start_km_service


class AddKmExcelPage:
    def __init__(self):
        help_text = load_markdown("../data/help_markdowns/add_km_excel_help.md")

        def build_content(container: Element):
            KmExcelTool(container)

        if is_km_service_running():
            ToolPanelWithHelp(
                title="Add KM to Excel",
                help_text=help_text,
                content_builder=build_content,
            )
        else:
            ui.label("❌ KM Service is not running. Please start the service.")
            with ui.row().classes("items-center gap-4"):
                start_button = ui.button("Start KM service")
                spinner = ui.spinner(size="lg").props("color=primary").classes("hidden")

            async def handle_start():
                start_button.disable()
                spinner.classes(remove="hidden")

                await start_km_service()

            start_button.on("click", handle_start)
