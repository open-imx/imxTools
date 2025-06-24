from nicegui import ui
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum

from apps.gui.helpers.io import spooled_file_to_temp_file
from src.imxTools.utils.helpers import get_situations


class ImxUpload:
    def __init__(self, label: str, on_change: callable = None):
        self.label = label
        self.on_change = on_change
        self.file_path = None
        self.situation = None

        with ui.card().classes("w-full"):
            ui.label(self.label).classes("font-bold")
            with ui.card_section().classes("w-full"):
                with ui.row().classes("w-full"):
                    self.file_input = (
                        ui.upload(
                            label="Upload IMX file",
                            auto_upload=True,
                            on_upload=self.handle_upload,
                            max_files=1,
                        )
                        .classes("w-full")
                        .style("flex: 1")
                    )

                with ui.row().classes("w-full"):
                    self.situation_dropdown = (
                        ui.select(
                            [],
                            label="Select Situation",
                            on_change=self._on_situation_change,
                        )
                        .classes("w-full")
                        .style("flex: 1")
                    )

        self.situation_dropdown.disable()

    def handle_upload(self, e):
        self.file_path = spooled_file_to_temp_file(e)
        suffix = self.file_path.suffix.lower()

        if suffix == ".zip":
            self.situation_dropdown.options = []
            self.situation_dropdown.disable()
            self.situation = None
        elif suffix == ".xml":
            situations = get_situations(self.file_path)
            if situations:
                self.situation_dropdown.options = [s.name for s in situations]
                self.situation_dropdown.enable()
                self.situation_dropdown.value = self.situation_dropdown.options[0]
                self.situation = ImxSituationEnum[self.situation_dropdown.value]
            else:
                self.situation_dropdown.options = []
                self.situation_dropdown.disable()
                self.situation = None

        if self.on_change:
            self.on_change(self.file_path, self.situation)

    def _on_situation_change(self, e):
        if e.value:
            self.situation = ImxSituationEnum[e.value]
        else:
            self.situation = None
        if self.on_change:
            self.on_change(self.file_path, self.situation)

    def get_value(self):
        return self.file_path, self.situation
