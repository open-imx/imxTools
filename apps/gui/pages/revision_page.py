from nicegui.element import Element

from apps.gui.components.tools.revisionTool import RevisionTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp


class RevisionPage:
    def __init__(self):
        help_text = """
        ### ℹ️ IMX Revision Help

        1. **Download the revision template** and fill in your changes.
        2. **Upload the IMX file** you want to modify.
        3. **Upload the filled-in Excel file**.
        4. Click **Apply Revisions** to generate a revised IMX package.

        Tip: You will receive a ZIP file containing the modified XML and a summary report.
        """

        def build_content(container: Element):
            RevisionTool(container)

        ToolPanelWithHelp(
            title="IMX Revision Tool",
            help_text=help_text,
            content_builder=build_content,
        )
