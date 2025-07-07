import asyncio
import tempfile
import zipfile
from pathlib import Path

from src.imxTools.insights.diff_and_population import write_diff_output_files
from src.imxTools.utils.helpers import create_timestamp
from nicegui import ui

from apps.gui.components.widgets.imxUpload import ImxUpload
from apps.gui.helpers.io import delete_later


class DiffTool:
    def __init__(self, container):
        with container:
            self.imx_t1 = ImxUpload(
                "Upload IMX File T1", on_change=self._on_upload_change
            )
            self.imx_t2 = ImxUpload(
                "Upload IMX File T2", on_change=self._on_upload_change
            )

            with ui.row():
                self.geojson_toggle = ui.switch("Generate GeoJSON?")
                self.wgs84_toggle = ui.switch("Convert to WGS84?")

                def update_wgs84_visibility():
                    self.wgs84_toggle.set_visibility(self.geojson_toggle.value)

                self.geojson_toggle.on(
                    "update:model-value", lambda e: update_wgs84_visibility()
                )
                update_wgs84_visibility()

            self.status_label = ui.label().classes("text-sm italic")
            ui.button("Run Comparison", on_click=self.run_diff).classes(
                "mt-4 btn-primary"
            )

    def _on_upload_change(self, file_path, situation):
        ui.notify(
            f"Uploaded: {file_path.name} | Situation: {situation.name if situation else 'None'}"
        )

    async def run_diff(self):
        ui.notify("Processing...", type="info")

        t1_path, t1_situation = self.imx_t1.get_value()
        t2_path, t2_situation = self.imx_t2.get_value()

        if not t1_path or not t2_path:
            ui.notify("Both IMX T1 and T2 files must be uploaded", type="negative")
            return

        try:
            geojson = self.geojson_toggle.value
            to_wgs = self.wgs84_toggle.value
            self.status_label.text = "Running comparison..."

            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "output"
                output_path.mkdir(parents=True, exist_ok=True)

                await asyncio.to_thread(
                    write_diff_output_files,
                    t1_path,
                    t2_path,
                    output_path,
                    t1_situation,
                    t2_situation,
                    geojson,
                    to_wgs,
                )

                zip_name = f"diff_{create_timestamp()}.zip"
                zip_path = Path(tempfile.gettempdir()) / zip_name
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file in output_path.rglob("*"):
                        zipf.write(file, file.relative_to(output_path))

                ui.download(zip_path, filename=zip_name)
                ui.notify("Diff report ready!", type="positive")
                self.status_label.text = "✅ Report zipped and ready to download!"

                asyncio.create_task(delete_later(zip_path))

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            self.status_label.text = "❌ Failed"
