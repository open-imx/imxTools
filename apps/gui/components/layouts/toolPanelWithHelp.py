from collections.abc import Callable

from nicegui import ui
from nicegui.element import Element


class ToolPanelWithHelp:
    def __init__(
        self,
        title: str,
        help_text: str,
        content_builder: Callable[[Element], None],
        help_visible=False,
    ):
        self.help_visible = help_visible
        help_ratio = 0.25
        help_ratio = max(0.1, min(help_ratio, 0.9))  # Clamp between 10% and 90%

        self._main_width = f"{(1 - help_ratio) * 80}%"
        self._help_width = f"{help_ratio * 80}%"

        with ui.element("div").classes("flex w-full h-full gap-4") as self.container:
            self.main_panel = (
                ui.column().style(f"width: {self._main_width};").classes("gap-4")
            )
            with self.main_panel:
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(title).classes("text-2xl font-bold")
                    self.help_button = (
                        ui.button(icon="help", on_click=self.toggle_help)
                        .props("flat")
                        .classes("text-primary")
                    )

                content_builder(self.main_panel)

            self.help_panel = (
                ui.column().style(f"width: {self._help_width};").classes("grow")
            )
            with self.help_panel:
                with ui.card().classes("w-full grow"):
                    with ui.row().classes("w-full justify-end"):
                        self.close_help_button = (
                            ui.button("✖", on_click=self.toggle_help)
                            .props("flat")
                            .classes("text-red-500")
                        )
                    ui.markdown(help_text).classes("text-sm")

        self._apply_visibility()

    def _apply_visibility(self):
        self.help_panel.set_visibility(self.help_visible)
        self.main_panel.style(
            "width: 100%;" if not self.help_visible else f"width: {self._main_width};"
        )
        self.help_button.set_visibility(not self.help_visible)
        self.close_help_button.set_visibility(self.help_visible)

    def toggle_help(self):
        self.help_visible = not self.help_visible
        self._apply_visibility()
