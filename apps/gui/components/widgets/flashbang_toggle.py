from nicegui import app, ui

# Global dark mode instance
dark_mode = ui.dark_mode()

def create_dark_mode_toggle(dark_mode: ui.dark_mode):
    saved_state = app.storage.user.get('dark_mode', True)
    dark_mode.enable() if saved_state else dark_mode.disable()

    def get_icon():
        return "fa-regular fa-sun" if dark_mode.value else "fa-regular fa-moon"

    icon = ui.icon(get_icon()).classes(
        'text-xl cursor-pointer hover:scale-110 transition-transform'
    ).tooltip('Toggle dark/light mode')

    def toggle_dark_light():
        dark_mode.toggle()
        app.storage.user['dark_mode'] = dark_mode.value
        icon.name = get_icon()

    icon.on('click', toggle_dark_light)
    return icon
