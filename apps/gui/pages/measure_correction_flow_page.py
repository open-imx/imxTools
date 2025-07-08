from nicegui.element import Element

from apps.gui.components.flows.measure_correction import MeasureCorrectionTool
from apps.gui.components.layouts.toolPanelWithHelp import ToolPanelWithHelp
from apps.gui.helpers.io import load_markdown


class MeasureCorrectionFlowPage:
    def __init__(self):
        help_text = load_markdown("../data/help_markdowns/measure_correction_help.md")

        def build_content(container: Element):
            MeasureCorrectionTool(container)

        ToolPanelWithHelp(
            title="IMX Measure Correction Flow",
            help_text=help_text,
            content_builder=build_content,
        )
