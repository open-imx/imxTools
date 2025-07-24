from nicegui import ui
from apps.gui.components.widgets.flashbang_toggle import create_dark_mode_toggle
from apps.gui.components.widgets.version_check_dialog import version_stage_warning, new_version_release_dialog

def build_header(menu) -> None:
    with ui.header().classes("bg-base-200 text-base-content shadow-md"):
        with ui.row().classes("w-full items-center justify-between"):

            with ui.row().classes("items-center gap-2 ml-2"):
                # Menu icon
                ui.icon('fa-solid fa-bars').classes(
                    "text-xl cursor-pointer hover:scale-110 transition-transform"
                ).on('click', lambda: menu.toggle())

                # Title
                ui.label("IMX Tools").classes(
                    "text-2xl font-bold cursor-pointer"
                ).on("click", lambda: ui.navigate.to("/"))

            with ui.row().classes("items-center mr-4 gap-2"):
                ui.timer(0, version_stage_warning, once=True)
                ui.timer(0, lambda: new_version_release_dialog(as_button=True), once=True)

                dark_mode = ui.dark_mode()
                create_dark_mode_toggle(dark_mode)
