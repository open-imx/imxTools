from nicegui.element import Element

from apps.gui.components.tools.populationTool import PopulationTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp


class PopulationPage:
    def __init__(self):
        help_text = """
        ### ℹ️ IMX Population Help

        1. **Upload an IMX file** to analyze.
        2. **Select a situation** (if applicable).
        3. **Choose export formats** (GeoJSON/WGS84).
        4. Click **Run Population Report** to start the process.

        Tip: The result will be zipped for download.
        """

        def build_content(container: Element):
            PopulationTool(container)

        ToolPanelWithHelp(
            title="IMX Population Tool",
            help_text=help_text,
            content_builder=build_content,
        )
