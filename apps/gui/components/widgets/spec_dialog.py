# apps/gui/components/widgets/spec_dialog.py
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List, Optional

from nicegui import ui


async def prompt_spec_choice_dialog(candidates: List[Path]) -> Optional[Path]:
    """
    Toont een dialog met radio-opties (spec-bestanden).
    Retourneert de gekozen Path of None wanneer geannuleerd.
    """
    # Zorg dat candidates strings zijn (voor radio) en bewaar mapping
    options = [str(p) for p in candidates]
    selected = {'value': options[0] if options else ''}

    fut: asyncio.Future[Optional[Path]] = asyncio.get_event_loop().create_future()

    with ui.dialog() as dialog, ui.card():
        ui.label('Kies een specificatiebestand').classes('text-lg font-semibold')
        ui.separator()
        ui.radio(options=options, value=selected['value'], on_change=lambda e: selected.update(value=e.value))
        ui.separator()
        with ui.row().classes('justify-end w-full'):
            ui.button('Annuleren', on_click=lambda: (dialog.close(), fut.set_result(None)))
            ui.button('Kiezen', on_click=lambda: (dialog.close(), fut.set_result(Path(selected['value'])))).props('color=primary')

    dialog.open()
    return await fut
