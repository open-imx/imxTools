from nicegui import ui


def create_dark_mode_toggle():
    dark_mode = ui.dark_mode()
    dark_mode.enable()

    def toggle_dark_light():
        dark_mode.toggle()
        toggle_button.text = "🔦" if dark_mode.value else "🌙"

    toggle_button = ui.button(
        "🔦" if dark_mode.value else "🌙",
        on_click=toggle_dark_light,
    )

    return toggle_button
