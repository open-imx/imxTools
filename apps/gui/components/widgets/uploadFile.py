from pathlib import Path
import tempfile

from nicegui import ui

from apps.gui.helpers.io import spooled_file_to_temp_file


class UploadFile:
    def __init__(self, label: str, on_change: callable = None, accept: str = ".xlsx"):
        self.file_path: Path | None = None
        self._on_change = on_change

        with ui.card().classes("w-full") as self.card:
            ui.label(label).classes("font-bold")
            with ui.card_section().classes("w-full") as self.section:
                with ui.row().classes("w-full") as self.row:
                    self.upload = (
                        ui.upload(
                            label="Upload File",
                            auto_upload=True,
                            on_upload=self._handle_upload,
                            multiple=False,
                        )
                        .props(f'accept="{accept}"')
                        .classes("w-full")
                        .style("flex: 1")
                    )

    async def _handle_upload(self, event):
        self.file_path = spooled_file_to_temp_file(event)

        if self._on_change:
            self._on_change(self.file_path)
