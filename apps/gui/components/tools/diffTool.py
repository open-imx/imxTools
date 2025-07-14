import asyncio
import tempfile
import zipfile
from pathlib import Path

from apps.gui.components.widgets.uploadImxFile import ImxUpload
from src.imxTools.insights.diff_and_population import write_diff_output_files
from src.imxTools.utils.helpers import create_timestamp
from nicegui import ui

from apps.gui.helpers.io import delete_later


class DiffTool:
    def __init__(self, container):
        with container:
            self.imx_t1 = ImxUpload(
                "Upload IMX File T1", on_change=self._on_upload_change
            )

            with ui.column().classes("w-full"):
                with ui.row().classes("w-full items-center gap-4"):
                    self.reuse_t1_toggle = ui.switch(
                        "Use same IMX for T2?", value=False
                    )
                    self.reuse_t1_toggle.on_value_change(self._update_t2_inputs)

                    self.t2_situation_picker = (
                        ui.select(options=[], label="Select Situation T2")
                        .props("outlined")
                        .classes("flex-grow")
                    )
                    self.t2_situation_picker.visible = False

                self.imx_t2_container = ui.column().classes("w-full")
                with self.imx_t2_container:
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

            ui.button("Run Comparison", on_click=self.run_diff).classes(
                "mt-4 btn-primary"
            )

    def _update_t2_inputs(self, event):
        show_picker = bool(event.value)
        self.imx_t2_container.visible = not show_picker
        self.t2_situation_picker.visible = show_picker

        # ✅ If the user switches toggle ON later, ensure the picker is populated
        if show_picker:
            self._sync_t2_picker_with_t1()

    def _on_upload_change(self, file_path, situation):
        ui.notify(
            f"Uploaded: {file_path.name} | Situation: {situation.name if situation else 'None'}"
        )

        # ✅ Always update picker if reuse is ON
        if self.reuse_t1_toggle.value:
            self._sync_t2_picker_with_t1()

    def _sync_t2_picker_with_t1(self):
        t1_options = self.imx_t1.situation_options
        t1_value = self.imx_t1.situation_options_value

        if not t1_options:
            self.t2_situation_picker.set_options([])
            return

        # Pick a different default if possible
        t2_value = None
        for opt in t1_options:
            if opt != t1_value:
                t2_value = opt
                break

        self.t2_situation_picker.set_options(t1_options, value=t2_value or t1_value)

    async def run_diff(self):
        ui.notify("Processing...", type="info")

        t1_path, t1_situation = self.imx_t1.get_value()

        if self.reuse_t1_toggle.value:
            t2_path = t1_path
            t2_situation = self.t2_situation_picker.value
        else:
            t2_path, t2_situation = self.imx_t2.get_value()

        if not t1_path or not t2_path:
            ui.notify("Both IMX T1 and T2 files must be uploaded", type="negative")
            return

        if self.reuse_t1_toggle.value and not t2_situation:
            ui.notify("Select a situation for T2", type="negative")
            return

        try:
            geojson = self.geojson_toggle.value
            to_wgs = self.wgs84_toggle.value

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

                asyncio.create_task(delete_later(zip_path))

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
