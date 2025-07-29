import asyncio
import tempfile
from pathlib import Path

from nicegui import ui
from nicegui.element import Element

from apps.gui.components.widgets.uploadFile import UploadFile
from imxTools.utils.km_service_manager import get_km_service
from apps.gui.helpers.io import delete_later
from imxTools.utils.kmExcelProcessor import KmExcelProcessor


class KmExcelTool:
    def __init__(self, container: Element):
        with container:
            ui.label("📄 Add KM to Excel").classes("font-bold text-lg")

            self.input_upload = UploadFile(
                "Upload Excel (.xlsx)", on_change=self._on_input_upload
            )

            self.simple_checkbox = ui.checkbox(
                "Use simple display value only", value=True
            ).classes("mt-2")

            with ui.row():
                self.process_button = ui.button(
                    "Add KM", on_click=self.run_add_km
                ).classes("btn-primary mt-4")
                self.spinner = (
                    ui.spinner(size="lg").props("color=primary").classes("hidden mt-2")
                )

        self.input_file: Path | None = None

    def _on_input_upload(self, file_path: Path):
        self.input_file = file_path
        ui.notify(f"Uploaded file: {file_path.name}", type="positive")

    async def run_add_km(self):
        if not self.input_file:
            ui.notify("Please upload an Excel file first.", type="warning")
            return

        self.process_button.disable()
        self.spinner.classes(remove="hidden")

        try:
            temp_output = (
                Path(tempfile.gettempdir()) / f"km_result_{self.input_file.stem}.xlsx"
            )
            if temp_output.exists():
                temp_output.unlink()

            processor = KmExcelProcessor(get_km_service(), use_simple=self.simple_checkbox.value)

            await asyncio.to_thread(
                processor.process, self.input_file, temp_output
            )

            ui.download(temp_output, filename=temp_output.name)
            ui.notify("✅ KM values added successfully.", type="positive")

            asyncio.create_task(delete_later(temp_output))

        except Exception as e:
            ui.notify(f"❌ Error: {e}", type="negative")
        finally:
            self.process_button.enable()
            self.spinner.classes(add="hidden")
