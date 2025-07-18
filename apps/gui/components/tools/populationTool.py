import asyncio
import tempfile
import zipfile
from pathlib import Path

from nicegui import ui
from nicegui.element import Element

from apps.gui.components.widgets.uploadImxFile import ImxUpload
from src.imxTools.insights.diff_and_population import write_population_output_files
from src.imxTools.utils.helpers import create_timestamp

from apps.gui.helpers.io import delete_later


class PopulationTool:
    def __init__(self, container: Element):
        with container:
            self.imx_upload = ImxUpload(
                "Upload IMX File", on_change=self._on_upload_change
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
            ui.button("Run Population Report", on_click=self.run_population).classes(
                "mt-4 btn-primary"
            )

    def _on_upload_change(self, file_path, situation):
        ui.notify(
            f"Uploaded: {file_path.name} | Situation: {situation.name if situation else 'None'}"
        )

    async def run_population(self):
        ui.notify("Processing...", type="info")

        imx_path, imx_situation = self.imx_upload.get_value()

        if not imx_path:
            ui.notify("Please upload an IMX file", type="negative")
            return

        try:
            geojson = self.geojson_toggle.value
            to_wgs = self.wgs84_toggle.value
            self.status_label.text = "Generating population report..."

            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "output"
                output_path.mkdir(parents=True, exist_ok=True)

                await asyncio.to_thread(
                    write_population_output_files,
                    imx_path,
                    output_path,
                    imx_situation,
                    geojson,
                    to_wgs,
                )

                zip_name = f"population_{create_timestamp()}.zip"
                zip_path = Path(tempfile.gettempdir()) / zip_name
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file in output_path.rglob("*"):
                        zipf.write(file, file.relative_to(output_path))

                ui.download(zip_path, filename=zip_name)
                ui.notify("Population report ready!", type="positive")
                self.status_label.text = "✅ Report zipped and ready to download!"

                asyncio.create_task(delete_later(zip_path))

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            self.status_label.text = "❌ Failed"
