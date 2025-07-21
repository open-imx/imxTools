from nicegui.element import Element

from apps.gui.components.tools.populationTool import PopulationTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp
from apps.gui.helpers.io import load_markdown


class PopulationPage:
    def __init__(self):
        help_text = load_markdown("../data/help_markdowns/population_tool_help.md")


        def build_content(container: Element):
            PopulationTool(container)

        ToolPanelWithHelp(
            title="IMX Population Tool",
            help_text=help_text,
            content_builder=build_content,
        )
