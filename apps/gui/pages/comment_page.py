from apps.gui.components.tools.commentsTool import CommentsTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp


class CommentPage:
    def __init__(self):
        help_text = """
        ### ℹ️ ....
        """

        def build_diff_content(container):
            CommentsTool(container)

        ToolPanelWithHelp(
            title="IMX Comments Tool",
            help_text=help_text,
            content_builder=build_diff_content,
            help_visible=False,  # Optional: Set to True to show help by default
        )
