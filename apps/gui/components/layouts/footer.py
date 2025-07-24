import importlib.metadata
from nicegui import ui
from src.imxTools import __version__ as imx_tools_version

def build_footer():
    with ui.footer().style("background-color: #3874c8"):
        with ui.column().classes("gap-0 p-0"):
            ui.label(f"ImxTools v{imx_tools_version}").classes("text-lg m-0").style("line-height: 1")
            ui.label(f"using ImxInsights v{importlib.metadata.version('imxInsights')}").classes("text-xs mt-1").style("line-height: 1")
