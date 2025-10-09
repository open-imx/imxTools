# apps/gui/components/tools/populationTool.py
from __future__ import annotations

import asyncio
import tempfile
import zipfile
from pathlib import Path

from nicegui import ui
from nicegui.element import Element

from apps.gui.components.widgets.uploadImxFile import ImxUpload
from apps.gui.components.widgets.specFile import SpecFilePicker
from apps.gui.components.widgets.spec_dialog import prompt_spec_choice_dialog
from src.imxTools.insights.diff_and_population import write_population_output_files
from src.imxTools.utils.helpers import create_timestamp
from src.imxTools.utils.spec_resolver import NeedUserSpecChoice, auto_pick_spec_or_raise
from apps.gui.helpers.io import delete_later, APP_RUN_PATH


class PopulationTool:
    def __init__(self, container: Element):
        with container:
            # ---------- IMX uploader ----------
            self.imx_upload = ImxUpload(
                "Upload IMX File", on_change=self._on_imx_upload_change
            )

            # ---------- GeoJSON / WGS84 toggles ----------
            with ui.row():
                self.geojson_toggle = ui.switch("Generate GeoJSON?")
                self.wgs84_toggle = ui.switch("Convert to WGS84?")

                def update_wgs84_visibility():
                    self.wgs84_toggle.set_visibility(self.geojson_toggle.value)

                self.geojson_toggle.on(
                    "update:model-value", lambda e: update_wgs84_visibility()
                )
                update_wgs84_visibility()

            # ---------- Status + Run button ----------
            ui.button("Run Population Report", on_click=self.run_population).classes(
                "mt-4 btn-primary"
            )

            # ---------- Spec file picker ----------
            self.spec_picker = SpecFilePicker(
                on_change=self._on_imx_spec_upload_change,
            )

    # ---------- Handlers ----------

    @staticmethod
    def _on_imx_upload_change(file_path, situation):
        ui.notify(
            f"Uploaded: {file_path.name} | Situation: {situation.name if situation else 'None'}"
        )

    @staticmethod
    def _on_imx_spec_upload_change(file_path):
        if file_path:
            ui.notify(f"Uploaded: {file_path.name}")

    # ---------- Run Population ----------
    async def run_population(self):
        imx_path, imx_situation = self.imx_upload.get_value()
        spec_file = self.spec_picker.get_value()  # only non-None in 'pick' mode
        mode = self.spec_picker.get_mode()        # 'none' | 'auto' | 'pick'

        if not imx_path:
            ui.notify("Please upload an IMX file", type="negative")
            return

        # Map the mode -> chosen_spec value expected by write_population_output_files
        if mode == "auto":
            chosen_spec = "AUTO"
            if self.spec_picker.auto_version_select.value != "Detect automatically":
                try:
                    chosen_spec = auto_pick_spec_or_raise([self.spec_picker.auto_version_select.value], Path(APP_RUN_PATH) / "specifications")
                    if not chosen_spec:
                        ui.notify(
                            f"Could not find a specification file for version {self.spec_picker.auto_version_select.value}, try to auto detect a spec file",
                            type="negative"
                        )
                except NeedUserSpecChoice as ex:
                    # Triggered when chosen_spec == "AUTO" and multiple candidates found
                    choice = await prompt_spec_choice_dialog(ex.candidates)
                    if not choice:
                        ui.notify("Cancelled: no specification selected.", type="warning")
                        return
                    chosen_spec = choice

        elif mode == "pick":
            if not spec_file:
                ui.notify("Please upload a specification CSV or choose Auto/None.", type="negative")
                return
            chosen_spec = spec_file
        else:  # mode == "none"
            chosen_spec = None

        try:
            geojson = self.geojson_toggle.value
            to_wgs = self.wgs84_toggle.value

            ui.notify("Generating population report...", type="info")

            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "output"
                output_path.mkdir(parents=True, exist_ok=True)

                while True:
                    try:
                        msg = await asyncio.to_thread(
                            write_population_output_files,
                            imx_path,
                            output_path,
                            imx_situation,
                            geojson,
                            to_wgs,
                            chosen_spec,  # Path | "AUTO" | None
                            Path(f"{APP_RUN_PATH}/specifications"),
                        )
                        if msg:
                            ui.notify(msg, type="negative")
                            return
                        break

                    except NeedUserSpecChoice as ex:
                        # Only triggered when chosen_spec == "AUTO" and multiple candidates are found
                        choice = await prompt_spec_choice_dialog(ex.candidates)
                        if not choice:
                            ui.notify("Geannuleerd: geen specificatie gekozen.", type="warning")
                            return
                        chosen_spec = choice
                        continue

                    except ValueError as ev:
                        ui.notify(f"{ev}, will not add specs to report!", type="warning")
                        chosen_spec = None

                zip_name = f"population_{create_timestamp()}.zip"
                zip_path = Path(tempfile.gettempdir()) / zip_name
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file in output_path.rglob("*"):
                        zipf.write(file, file.relative_to(output_path))

                ui.download(zip_path, filename=zip_name)
                ui.notify("Population report ready!", type="positive")
                ui.notify("✅ Report zipped and ready to download!", type="positive")

                asyncio.create_task(delete_later(zip_path))

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
