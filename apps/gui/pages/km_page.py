from nicegui.element import Element

from apps.gui.components.tools.kmTool import KmTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp


class KmPage:
    def __init__(self):
        help_text = """
        ### ℹ️ IMX KM Lookup Help

        1. **Enter X and Y** coordinates _or_ paste a **GML Point** string.
        2. Click **Resolve KM** to find matching kilometer values.
        3. Results will include the KM value and the associated `lint_name`.

        Tip: Coordinates should be in the CRS expected by the backend resolver.
        """

        def build_content(container: Element):
            KmTool(container)

        ToolPanelWithHelp(
            title="IMX KM Lookup",
            help_text=help_text,
            content_builder=build_content,
        )
