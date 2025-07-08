import asyncio
from pathlib import Path
import tempfile

from nicegui import ui
from nicegui.element import Element

from apps.gui.components.widgets.uploadFile import UploadFile
from src.imxTools.comments.comments_extractor import extract_comments_to_new_sheet
from src.imxTools.comments.comments_replacer import apply_comments_from_issue_list

from apps.gui.helpers.io import delete_later


class CommentsTool:
    def __init__(self, container: Element):
        with container:
            with ui.tabs().classes("w-full") as tabs:
                extract_tab = ui.tab("Extract")
                reproject_tab = ui.tab("Reproject")

            with ui.tab_panels(tabs, value=extract_tab).classes("w-full"):
                with ui.tab_panel(extract_tab):
                    self._build_extract_tab()
                with ui.tab_panel(reproject_tab):
                    self._build_reproject_tab()

    def _build_extract_tab(self):
        ui.label("Extract Comments").classes("font-bold")

        self.input_upload = UploadFile(
            "Upload Diff Report (.xlsx)", on_change=self._on_input_upload
        )

        with ui.row().classes("items-center gap-4 mt-2"):
            self.add_to_wb_checkbox = ui.checkbox(
                "Add to existing workbook (new sheet)",
                on_change=self._on_add_to_wb_change,
            )
            self.overwrite_checkbox = ui.checkbox("Overwrite sheet if it exists").props(
                'hint="Only applies when adding sheet to existing workbook."'
            )
            self.overwrite_checkbox.visible = False

        ui.button("Extract Comments", on_click=self.run_extract).classes(
            "btn-primary mt-2"
        )

        self.status_label_extract = ui.label().classes("text-sm italic mt-4")

        self.input_file = None

    def _build_reproject_tab(self):
        ui.label("Reproject Comments").classes("font-bold")

        self.new_diff_upload = UploadFile(
            "Upload New Diff Report (.xlsx)", on_change=self._on_new_diff_upload
        )
        self.comment_list_upload = UploadFile(
            "Upload Comment List (.xlsx)", on_change=self._on_comment_list_upload
        )

        ui.button("Reproject Comments", on_click=self.run_reproject).classes(
            "btn-primary mt-2"
        )

        self.status_label_reproject = ui.label().classes("text-sm italic mt-4")

        self.new_diff_file = None
        self.comment_list_file = None

    def _on_input_upload(self, file_path: Path):
        self.input_file = file_path
        ui.notify(f"Uploaded diff report: {file_path.name}")

    def _on_new_diff_upload(self, file_path: Path):
        self.new_diff_file = file_path
        ui.notify(f"Uploaded new diff report: {file_path.name}")

    def _on_comment_list_upload(self, file_path: Path):
        self.comment_list_file = file_path
        ui.notify(f"Uploaded comment list: {file_path.name}")

    def _on_add_to_wb_change(self):
        self.overwrite_checkbox.visible = self.add_to_wb_checkbox.value

    async def run_extract(self):
        if not self.input_file:
            ui.notify("Please upload a diff report first.", type="warning")
            return

        self.status_label_extract.text = "Extracting comments..."
        try:
            temp_file = (
                Path(tempfile.gettempdir())
                / f"comments_extracted_{self.input_file.stem}.xlsx"
            )
            if temp_file.exists():
                temp_file.unlink()

            await asyncio.to_thread(
                extract_comments_to_new_sheet,
                self.input_file,
                str(temp_file),
                add_to_wb=self.add_to_wb_checkbox.value,
                overwrite=self.overwrite_checkbox.value
                if self.add_to_wb_checkbox.value
                else False,
            )

            ui.download(temp_file, filename=temp_file.name)
            ui.notify("Comments extracted successfully!", type="positive")
            self.status_label_extract.text = "✅ Comments extraction complete."

            asyncio.create_task(delete_later(temp_file))

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            self.status_label_extract.text = "❌ Extraction failed."

    async def run_reproject(self):
        if not self.new_diff_file or not self.comment_list_file:
            ui.notify(
                "Please upload both new diff report and comment list.",
                type="warning",
            )
            return

        self.status_label_reproject.text = "Applying comments..."
        try:
            temp_file = (
                Path(tempfile.gettempdir())
                / f"comments_reprojected_{self.new_diff_file.stem}.xlsx"
            )
            if temp_file.exists():
                temp_file.unlink()

            await asyncio.to_thread(
                apply_comments_from_issue_list,
                issue_list_path=self.comment_list_file,
                new_diff_path=self.new_diff_file,
                output_path=str(temp_file),
            )

            ui.download(temp_file, filename=temp_file.name)
            ui.notify("Comments applied successfully!", type="positive")
            self.status_label_reproject.text = "✅ Reprojection complete."

            asyncio.create_task(delete_later(temp_file))

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
            self.status_label_reproject.text = "❌ Reprojection failed."
