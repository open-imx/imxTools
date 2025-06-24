from apps.gui.components.tools.diffTool import DiffTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp


class DiffPage:
    def __init__(self):
        help_text = """
        ### ℹ️ IMX Diff Help

        1. **Upload T1 and T2** IMX files.
        2. **Select a situation** if using XML.
        3. **Use toggles** to export extra formats.
        4. Click **Run Comparison** to generate results.

        Tip: You can use `.zip` files without situation selection.
        """

        def build_diff_content(container):
            DiffTool(container)

        ToolPanelWithHelp(
            title="IMX Diff Tool",
            help_text=help_text,
            content_builder=build_diff_content,
            help_visible=False,  # Optional: Set to True to show help by default
        )
