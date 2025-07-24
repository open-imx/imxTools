from nicegui import ui

from apps.gui.components.layouts.drawer_left import build_drawer
from apps.gui.components.layouts.footer import build_footer
from apps.gui.components.layouts.header import build_header


async def create_layout():
    ui.add_head_html(
        '<link rel="stylesheet" '
        'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.0/css/all.min.css" '
        'crossorigin="anonymous" referrerpolicy="no-referrer" />',
        shared=True
    )
    menu = build_drawer()
    build_header(menu)
    build_footer()
