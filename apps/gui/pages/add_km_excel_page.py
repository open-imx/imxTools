from nicegui import ui
from nicegui.element import Element

from apps.gui.components.tools.kmExcelTool import KmExcelTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp
from apps.gui.helpers.km_service_manager import is_km_service_running, start_km_service


class AddKmExcelPage:
    def __init__(self):
        help_text = """
        ### 📄 Add KM to Excel — How to Use

        This tool lets you **upload an Excel file** containing **GML coordinates**  
        and automatically resolves **KM values** for each matching row.

        #### ✅ Steps to use:
        1. **Prepare your Excel**
           - Make sure your sheet has at least one column ending with **`gml:coordinates`**.
           - Example: Location.GeographicLocation.gml:Point.gml:coordinates

        2. **Upload your Excel**
           - Upload an `.xlsx` file with your data.

        3. **Process & Download**
           - The tool finds each GML point, resolves KM,
             and adds **`km_value_x`** and **`km_lint_x`** columns.
           - If no KM could be found, the lint column will contain a message.
           - Download the updated file when ready.

        #### ℹ️ Notes
        - The KM lookup uses the same service as the coordinate KM tool.
        - Supports multiple results per row.
        """

        def build_content(container: Element):
            KmExcelTool(container)

        # ToolPanelWithHelp(
        #     title="Add KM to Excel",
        #     help_text=help_text,
        #     content_builder=build_content,
        # )

        if is_km_service_running():
            ToolPanelWithHelp(
                title="Add KM to Excel",
                help_text=help_text,
                content_builder=build_content,
            )
        else:
            ui.label("❌ KM Service is not running. Please start the service.")
            with ui.row().classes('items-center gap-4'):
                start_button = ui.button("Start KM service")
                spinner = ui.spinner(size='lg').props('color=primary').classes('hidden')

            async def handle_start():
                start_button.disable()
                spinner.classes(remove='hidden')

                await start_km_service()

            start_button.on('click', handle_start)
