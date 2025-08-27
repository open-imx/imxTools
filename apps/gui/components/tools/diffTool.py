import asyncio
import tempfile
import zipfile
from pathlib import Path

from apps.gui.components.widgets.uploadFile import UploadFile
from apps.gui.components.widgets.uploadImxFile import ImxUpload
from src.imxTools.insights.diff_and_population import write_diff_output_files
from src.imxTools.utils.helpers import create_timestamp
from nicegui import ui

from apps.gui.helpers.io import delete_later


class DiffTool:
    def __init__(self, container):
        with container:
            self.imx_t1 = ImxUpload(
                "Upload IMX File T1", on_change=self._on_t1_upload_change
            )

            with ui.column().classes("w-full"):
                with ui.row().classes("w-full items-center gap-4"):
                    self.reuse_t1_toggle = ui.switch(
                        "Use same IMX for T2?", value=False
                    ).tooltip("Disabled when T1 is a IMX container (zip)")
                    self.reuse_t1_toggle.on_value_change(self._update_t2_inputs)

                    self.t2_situation_picker = (
                        ui.select(options=[], label="Select Situation T2")
                        .props("outlined")
                        .classes("flex-grow")
                    )
                    self.t2_situation_picker.visible = False

                self.imx_t2_container = ui.column().classes("w-full")
                with self.imx_t2_container:
                    # T2 uploader (separate handler)
                    self.imx_t2 = ImxUpload(
                        "Upload IMX File T2", on_change=self._on_t2_upload_change
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

            ui.separator()
            ui.label("Upload IMX Spec file (Optional) ").classes("italic")
            ui.link(
                "See docs for more information",
                "https://open-imx.github.io/imxInsights/reference/utils/header_annotator/#imxInsights.utils.headerAnnotator.HeaderSpec--specification-csv",
                new_tab=True,
            )
            with ui.row().classes("w-full items-center gap-2"):
                self.imx_spec = UploadFile(
                    "Upload IMX Spec (.csv)",
                    on_change=self._on_imx_spec_upload_change,
                    accept=".csv",
                )

            ui.button("Run Comparison", on_click=self.run_diff).classes(
                "mt-4 btn-primary"
            )


    def _on_t1_upload_change(self, file_path: Path | None, situation):
        """Handle T1 uploads; disable 'reuse' when a ZIP is used."""
        if file_path:
            ui.notify(
                f"Uploaded (T1): {file_path.name} | Situation: {situation.name if situation else 'None'}"
            )
            is_zip = file_path.suffix.lower() == ".zip"

            if is_zip:
                # Force OFF and disable the toggle until T1 is changed away from ZIP
                if self.reuse_t1_toggle.value:
                    self.reuse_t1_toggle.set_value(False)
                    # ensure UI reflects T2 inputs for 'False'
                    self._update_t2_inputs(type("E", (), {"value": False}))
                self.reuse_t1_toggle.disable()
                self.reuse_t1_toggle.tooltip("Disabled because T1 is a ZIP")
            else:
                # Non-ZIP: allow user to choose reuse again
                self.reuse_t1_toggle.enable()
                self.reuse_t1_toggle.tooltip("Use same IMX for T2?")

        else:
            # T1 cleared: re-enable choice
            self.reuse_t1_toggle.enable()
            self.reuse_t1_toggle.tooltip("Use same IMX for T2?")

        # Keep T2 picker in sync when reuse is on
        if self.reuse_t1_toggle.value:
            self._sync_t2_picker_with_t1()

    def _on_t2_upload_change(self, file_path: Path | None, situation):
        if file_path:
            ui.notify(
                f"Uploaded (T2): {file_path.name} | Situation: {situation.name if situation else 'None'}"
            )
        else:
            ui.notify("Cleared T2 file")

    @staticmethod
    def _on_imx_spec_upload_change(file_path: Path | None):
        if file_path:
            ui.notify(f"Uploaded: {file_path.name}")

    def _update_t2_inputs(self, event):
        show_picker = bool(event.value)
        self.imx_t2_container.visible = not show_picker
        self.t2_situation_picker.visible = show_picker
        if show_picker:
            self._sync_t2_picker_with_t1()

    def _sync_t2_picker_with_t1(self):
        t1_options = self.imx_t1.situation_options
        t1_value = self.imx_t1.situation_options_value

        if not t1_options:
            self.t2_situation_picker.set_options([])
            return

        # Pick a different default if possible
        t2_value = next((opt for opt in t1_options if opt != t1_value), None)
        self.t2_situation_picker.set_options(t1_options, value=t2_value or t1_value)

    async def run_diff(self):
        ui.notify("Processing...", type="info")

        t1_path, t1_situation = self.imx_t1.get_value()
        spec_file = self.imx_spec.get_value() if self.imx_spec else None

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
                    False,
                    spec_file,
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
