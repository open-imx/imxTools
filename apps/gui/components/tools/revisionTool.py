import asyncio
import shutil
import tempfile
from pathlib import Path

from apps.gui.components.widgets.metadataSettingsUi import MetadataSettingsUI
from src.imxTools.revision.input_validation import validate_process_input
from src.imxTools.revision.process_revision import process_imx_revisions
from src.imxTools.revision.revision_template import get_revision_template
from nicegui import ui
from nicegui.element import Element

from apps.gui.helpers.io import spooled_file_to_temp_file, delete_later


class RevisionTool:
    def __init__(self, container: Element):
        with container:
            ui.button(
                "⬇ Download Revision Template", on_click=self.download_template
            ).classes("btn-outline w-80")

            with ui.card().classes("w-full"):
                ui.label("Apply Revisions").classes("font-bold")
                self.imx_upload = ui.upload(
                    label="Upload IMX XML",
                    auto_upload=True,
                    max_files=1,
                    on_upload=self._on_imx_upload,
                ).classes("w-full")
                self.excel_upload = ui.upload(
                    label="Upload Revision Excel File",
                    auto_upload=True,
                    max_files=1,
                    on_upload=self._on_excel_upload,
                ).classes("w-full")

                self.metadata_ui = MetadataSettingsUI()

                self.status_label = ui.label().classes("text-sm italic")
                ui.button("Apply Revisions", on_click=self.apply_revisions).classes(
                    "btn-primary mt-2"
                )

        self.imx_file = None
        self.excel_file = None

    def _on_imx_upload(self, e):
        self.imx_file = spooled_file_to_temp_file(e)
        ui.notify(f"IMX file uploaded: {self.imx_file.name}")

    def _on_excel_upload(self, e):
        self.excel_file = spooled_file_to_temp_file(e)
        ui.notify(f"Revision Excel uploaded: {self.excel_file.name}")

    async def download_template(self):
        try:
            temp_file = Path(tempfile.gettempdir()) / "revision-template.xlsx"
            if temp_file.exists():
                temp_file.unlink()

            await asyncio.to_thread(get_revision_template, temp_file)
            ui.download(temp_file, filename="revision-template.xlsx")
            asyncio.create_task(delete_later(temp_file))

        except Exception as e:
            ui.notify(f"Failed to generate template: {e}", type="negative")

    async def apply_revisions(self):
        if not self.imx_file or not self.excel_file:
            ui.notify("Please upload both IMX and Excel files", type="warning")
            return

        try:
            settings = self.metadata_ui.get_metadata_settings()

            self.status_label.text = "Running revision process..."
            with tempfile.TemporaryDirectory() as temp_dir:
                out_path = Path(temp_dir)
                await asyncio.to_thread(
                    validate_process_input, self.imx_file, self.excel_file, out_path
                )
                await asyncio.to_thread(
                    process_imx_revisions,
                    self.imx_file,
                    self.excel_file,
                    out_path,
                    settings.set_metadata,
                    settings.add_metadata,
                    settings.source,
                    settings.origin,
                    settings.set_parents,
                    settings.registration_time,
                    True,
                )

                zip_path = out_path.with_suffix(".zip")
                shutil.make_archive(zip_path.with_suffix(""), "zip", out_path)

                ui.download(zip_path, filename="revised_imx_package.zip")
                ui.notify("Revisions applied successfully!", type="positive")
                self.status_label.text = "✅ Modified IMX and report ready."

                asyncio.create_task(delete_later(zip_path))

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            self.status_label.text = "❌ Failed"
