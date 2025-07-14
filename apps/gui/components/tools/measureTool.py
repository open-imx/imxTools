import asyncio
import tempfile
from pathlib import Path
from nicegui import ui
from nicegui.element import Element

from apps.gui.components.widgets.uploadImxFile import ImxUpload
from src.imxTools.insights.measure_analyse import generate_measure_excel
from src.imxTools.utils.helpers import load_imxinsights_container_or_file

from apps.gui.helpers.io import delete_later


class MeasureTool:
    def __init__(self, container: Element):
        with container:
            self.imx_upload = ImxUpload(
                "Upload IMX File", on_change=self._on_upload_change
            )
            self.threshold_input = ui.number(label="Threshold", value=0.015).classes(
                "w-64"
            )

            self.status_label = ui.label().classes("text-sm italic")
            ui.button("Run Measure Check", on_click=self.run_measure_check).classes(
                "btn-primary"
            )

        self.file_path = None
        self.situation = None

    def _on_upload_change(self, file_path: Path, situation):
        self.file_path = file_path
        self.situation = situation
        ui.notify(
            f"Uploaded: {file_path.name} | Situation: {situation.name if situation else 'None'}"
        )

    async def run_measure_check(self):
        if not self.file_path:
            ui.notify("Please upload an IMX file first", type="warning")
            return

        try:
            self.status_label.text = "Running measure check..."
            threshold = self.threshold_input.value

            imx = await asyncio.to_thread(
                load_imxinsights_container_or_file, self.file_path, self.situation
            )

            temp_file = (
                Path(tempfile.gettempdir())
                / f"measure_output_{self.file_path.stem}.xlsx"
            )
            if temp_file.exists():
                temp_file.unlink()

            await asyncio.to_thread(
                generate_measure_excel, imx, temp_file, threshold if threshold else None
            )

            ui.download(temp_file, filename=temp_file.name)
            ui.notify("Measure check complete!", type="positive")
            self.status_label.text = "✅ Excel report ready to download."

            asyncio.create_task(delete_later(temp_file))

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            self.status_label.text = "❌ Failed"
