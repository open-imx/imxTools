# apps/gui/components/tools/diffTool.py
from __future__ import annotations

import asyncio
import tempfile
import zipfile
from pathlib import Path

from nicegui import ui

from apps.gui.components.widgets.spec_dialog import prompt_spec_choice_dialog
from apps.gui.components.widgets.uploadImxFile import ImxUpload
from apps.gui.components.widgets.specFile import SpecFilePicker
from apps.gui.helpers.io import delete_later, APP_RUN_PATH
from src.imxTools.insights.diff_and_population import write_diff_output_files
from src.imxTools.utils.helpers import create_timestamp
from src.imxTools.utils.spec_resolver import NeedUserSpecChoice, auto_pick_spec_or_raise


class DiffTool:
    def __init__(self, container):
        with container:
            # -------- T1 upload --------
            self.imx_t1 = ImxUpload(
                "Upload IMX File T1", on_change=self._on_t1_upload_change
            )

            # -------- T2 upload / reuse toggle --------
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
                    self.imx_t2 = ImxUpload(
                        "Upload IMX File T2", on_change=self._on_t2_upload_change
                    )

            # -------- GeoJSON toggles --------
            with ui.row():
                self.geojson_toggle = ui.switch("Generate GeoJSON?")
                self.wgs84_toggle = ui.switch("Convert to WGS84?")

                def update_wgs84_visibility():
                    self.wgs84_toggle.set_visibility(self.geojson_toggle.value)

                self.geojson_toggle.on(
                    "update:model-value", lambda e: update_wgs84_visibility()
                )
                update_wgs84_visibility()

            # -------- Run button --------
            ui.button("Run Comparison", on_click=self.run_diff).classes(
                "mt-4 btn-primary"
            )

            # -------- Spec file picker (reusable widget) --------
            self.spec_picker = SpecFilePicker(
                on_change=self._on_imx_spec_upload_change,
            )

    # ---------- Handlers ----------

    def _on_t1_upload_change(self, file_path: Path | None, situation):
        """Handle T1 uploads; disable 'reuse' when a ZIP is used."""
        if file_path:
            ui.notify(
                f"Uploaded (T1): {file_path.name} | Situation: {situation.name if situation else 'None'}"
            )
            is_zip = file_path.suffix.lower() == ".zip"

            if is_zip:
                if self.reuse_t1_toggle.value:
                    self.reuse_t1_toggle.set_value(False)
                    self._update_t2_inputs(type("E", (), {"value": False}))
                self.reuse_t1_toggle.disable()
                self.reuse_t1_toggle.tooltip("Disabled because T1 is a ZIP")
            else:
                self.reuse_t1_toggle.enable()
                self.reuse_t1_toggle.tooltip("Use same IMX for T2?")
        else:
            self.reuse_t1_toggle.enable()
            self.reuse_t1_toggle.tooltip("Use same IMX for T2?")

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

        t2_value = next((opt for opt in t1_options if opt != t1_value), None)
        self.t2_situation_picker.set_options(t1_options, value=t2_value or t1_value)

    # ---------- Run Diff ----------
    async def run_diff(self):
        ui.notify("Processing...", type="info")

        t1_path, t1_situation = self.imx_t1.get_value()
        spec_file = self.spec_picker.get_value()   # only non-None when mode == "pick"
        mode = self.spec_picker.get_mode()         # "none" | "auto" | "pick"

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

        # Map radio mode to the value expected by write_diff_output_files
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

            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "output"
                output_path.mkdir(parents=True, exist_ok=True)

                while True:
                    try:
                        await asyncio.to_thread(
                            write_diff_output_files,
                            t1_path,
                            t2_path,
                            output_path,
                            t1_situation,
                            t2_situation,
                            geojson,
                            to_wgs,
                            False,             # keep your existing flag as-is
                            chosen_spec,       # Path | "AUTO" | None
                            Path(f"{APP_RUN_PATH}/specifications"),
                        )
                        break
                    except NeedUserSpecChoice as ex:
                        # Triggered when chosen_spec == "AUTO" and multiple candidates found
                        choice = await prompt_spec_choice_dialog(ex.candidates)
                        if not choice:
                            ui.notify("Cancelled: no specification selected.", type="warning")
                            return
                        print()
                        chosen_spec = choice
                        continue

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
