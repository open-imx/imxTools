from nicegui import ui
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum

from apps.gui.components.widgets.uploadFile import UploadFile
from src.imxTools.utils.helpers import get_situations
from apps.gui.helpers.io import spooled_file_to_temp_file


class ImxUpload(UploadFile):
    def __init__(self, label: str, on_change: callable = None):
        # Accept XML and ZIP, and enforce extensions
        super().__init__(
            label,
            accept=".xml,.zip",
            enforce_extensions=True,
            on_change=self._imx_on_change,
        )
        self.situation = None
        self._user_on_change = on_change

        with self.section:
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

    async def _handle_upload(self, event):
        self.file_path = spooled_file_to_temp_file(event)
        suffix = self.file_path.suffix.lower()

        if self.enforce_extensions and suffix not in self.accept:
            ui.notify(
                f"Invalid file type: {suffix} (Allowed: {self.accept})", type="negative"
            )
            self.file_path.unlink(missing_ok=True)
            self.file_path = None
            return

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

        if self._user_on_change:
            self._user_on_change(self.file_path, self.situation)

    def _imx_on_change(self, file_path):
        # Handled in _handle_upload instead
        pass

    def _on_situation_change(self, e):
        if e.value:
            self.situation = ImxSituationEnum[e.value]
        else:
            self.situation = None
        if self._user_on_change:
            self._user_on_change(self.file_path, self.situation)

    def get_value(self):
        return self.file_path, self.situation

    @property
    def situation_options(self):
        return self.situation_dropdown.options

    @property
    def situation_options_value(self):
        return self.situation_dropdown.value
