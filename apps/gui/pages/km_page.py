from nicegui import ui

from nicegui.element import Element

from apps.gui.components.tools.kmTool import KmTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp
from apps.gui.helpers.km_service_manager import is_km_service_running, start_km_service


class KmPage:
    def __init__(self):
        help_text = """
        ### 📍 KM Lookup — How to Use

        This tool helps you resolve **kilometer values (KM)** for any given coordinate.

        #### ✅ Steps to use:
        1. **Input Coordinates**
           - Enter **X** and **Y** directly (in RD or WGS84, depending on mode).
           - _or_ Paste a **comma-separated pair** like `233592,581094`.
           - _or_ Paste a **GML Point**, e.g. `<gml:coordinates>233592.000,581094.000</gml:coordinates>`.

        2. **Select Coordinate System**
           - By default, coordinates are in **RD Amersfoort** (EPSG:28992).
           - Check **Use WGS84 (lat/lon)** to switch to global longitude/latitude (EPSG:4326).

        3. **Click on the Map**
           - You can also select a point directly by clicking on the map.

        4. **Resolve KM**
           - Click **Resolve KM** to look up the kilometer value(s) for your point.
           - The results will show the resolved **KM** value and the corresponding **line name**.

        #### ℹ️ Notes
        - The map marker updates automatically when you change coordinates.
        - The tool converts between RD and WGS84 automatically as needed.
        - Click **Resolve KM** again any time you adjust the location.
        """

        def build_content(container: Element):
            KmTool(container)

        if is_km_service_running():
            ToolPanelWithHelp(
                title="KM Lookup",
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
