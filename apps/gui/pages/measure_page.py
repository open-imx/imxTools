from nicegui.element import Element

from apps.gui.components.tools.measureTool import MeasureTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp


class MeasurePage:
    def __init__(self):
        help_text = """
        ### ℹ️ IMX Measure Check Help

        1. **Upload an IMX file** to check for measure consistency.
        2. **Adjust the threshold** if needed (default is 0.015).
        3. Click **Run Measure Check** to generate the Excel report.

        Tip: This tool analyzes measure progression in topological order.
        """

        def build_content(container: Element):
            MeasureTool(container)

        ToolPanelWithHelp(
            title="IMX Measure Check",
            help_text=help_text,
            content_builder=build_content,
        )
