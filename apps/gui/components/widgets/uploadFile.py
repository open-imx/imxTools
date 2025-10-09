# apps/gui/components/widgets/uploadFile.py
from pathlib import Path
from nicegui import ui
from apps.gui.helpers.io import spooled_file_to_temp_file


class UploadFile:
    def __init__(
        self,
        label: str,
        on_change: callable = None,
        accept: str = ".xlsx",
        enforce_extensions: bool = True,
        max_files: int = 1,
    ):
        self.file_path: Path | None = None
        self._on_change = on_change
        self.accept = {ext.strip().lower() for ext in accept.split(",")}
        self.enforce_extensions = enforce_extensions

        with ui.card().classes("w-full") as self.card:
            # 🔧 Header row with label (left) and clear button (right)
            with ui.row().classes("w-full justify-between items-center"):
                ui.label(label).classes("font-bold")
                self.clear_btn = (
                    ui.button("CLEAR", on_click=self.clear)
                    .props("flat round dense")
                    .tooltip("Clear uploaded file")
                )
                self.clear_btn.visible = False  # hide until a file is uploaded

            # Body with the uploader
            with ui.card_section().classes("w-full") as self.section:
                self.upload = (
                    ui.upload(
                        label="Upload File",
                        auto_upload=True,
                        on_upload=self._handle_upload,
                        max_files=max_files,
                    )
                    .props(f'accept="{",".join(self.accept)}"')
                    .classes("w-full")
                    .style("flex: 1")
                )

    async def _handle_upload(self, event):
        # If the control is disabled, do nothing (extra guard)
        if getattr(self.upload, "disabled", False):
            return

        self.file_path = spooled_file_to_temp_file(event)
        suffix = self.file_path.suffix.lower()

        if self.enforce_extensions and suffix not in self.accept:
            ui.notify(
                f"Invalid file type: {suffix} (Allowed: {self.accept})", type="negative"
            )
            self.file_path.unlink(missing_ok=True)
            self.file_path = None
            self.clear_btn.visible = False
            return

        self.clear_btn.visible = True  # show clear button after upload

        if self._on_change:
            self._on_change(self.file_path)

    def clear(self):
        """Clear the uploaded file and notify listeners."""
        if self.file_path:
            try:
                self.file_path.unlink(missing_ok=True)
            except Exception:
                pass
        self.file_path = None

        # Reset the uploader widget on the frontend
        self.upload.run_method("reset")
        self.clear_btn.visible = False  # hide again

        if self._on_change:
            self._on_change(None)

    def get_value(self) -> Path | None:
        return self.file_path

    # ---- added for external control (SpecFilePicker uses these) ----
    def disable(self) -> None:
        """Disable the file uploader (prevents selecting or dropping files)."""
        self.upload.disable()
        # Optional: visually deemphasize the section
        # self.section.disable()  # uncomment if you want the whole section disabled

    def enable(self) -> None:
        """Enable the file uploader."""
        self.upload.enable()
        # self.section.enable()  # match the disable choice above

    def set_value(self, path: Path | None) -> None:
        """Programmatically set the current file (None to clear)."""
        if path is None:
            self.clear()
            return
        self.file_path = path
        self.clear_btn.visible = True
        if self._on_change:
            self._on_change(self.file_path)
