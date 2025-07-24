from nicegui import ui

ui.add_head_html(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.0/css/all.min.css" integrity="sha512-…" crossorigin="anonymous" referrerpolicy="no-referrer" />',
    shared=True
)

def create_dark_mode_toggle():
    dark_mode = ui.dark_mode()
    dark_mode.enable()

    def get_icon():
        return "fa-regular fa-sun" if dark_mode.value else "fa-regular fa-moon"

    icon = ui.icon(get_icon()).classes('text-xl') \
        .classes('text-xl cursor-pointer hover:scale-110 transition-transform') \
        .tooltip('Flash bang')

    def toggle_dark_light():
        dark_mode.toggle()
        icon.name = (get_icon())

    icon.on('click', toggle_dark_light)
    return icon
