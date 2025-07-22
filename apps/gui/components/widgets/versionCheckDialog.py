import re
import emoji

from nicegui import ui

from imxTools.utils.version_check import GitHubRelease
from src.imxTools.utils.version_check import fetch_newer_releases, is_non_production_version
from src.imxTools import __version__ as tool_version

def normalize_markdown(notes: str) -> str:
    lines = notes.splitlines()
    cleaned = []

    for line in lines:
        # Remove lines with "by @user in https://..."
        if re.search(r"by\s+@\w[\w-]*\s+in\s+https?://\S+", line):
            line = "\n" + line.split("by @")[0] + "\n"

        # Replace markdown headers (## or ###) with bolded text
        line = re.sub(r"^(#{1,6})\s*(.+)", r"**\2**", line)

        if "Full Changelog" in line:
            continue

        cleaned.append(line)

    return emoji.emojize("\n".join(cleaned).strip(), language="alias")



async def version_stage_warning():
    if is_non_production_version(tool_version):
        with ui.row().classes(
            "fixed top-0 left-1/2 -translate-x-1/2 z-50 bg-yellow-200 text-black px-4 py-2 shadow-lg rounded-b-xl items-center"
        ):
            ui.label(f"⚠ You are running a non-production version: 🚀{tool_version}").classes("font-semibold")



async def new_version_release_dialog(include_pre_releases: bool = True, as_button: bool = False):
    releases = await fetch_newer_releases(
        repo_url="https://api.github.com/repos/open-imx/imxTools/releases",
        current_version_str=tool_version,
        include_pre_releases=include_pre_releases
    )

    if not releases:
        return

    normal_releases = [r for r in releases if not r.is_pre_release]
    pre_releases = [r for r in releases if r.is_pre_release]

    if as_button:
        # Set color: orange for only pre-releases, red if at least one normal release
        button_color = 'bg-orange' if pre_releases and not normal_releases else 'bg-red'
        text_color = 'text-black' if pre_releases and not normal_releases else 'bg-white'

        ui.button(
            icon='warning',
            text='New version available!',
            on_click=lambda: _new_version_release_dialog(releases),
        ).props('glossy push rounded').classes(
            f'text-lg font-bold uppercase {text_color} border-2 border-black {button_color}'
        )
    else:
        await _new_version_release_dialog(releases)


async def _new_version_release_dialog(available_releases: list["GitHubRelease"]):

    normal_releases = [r for r in available_releases if not r.is_pre_release]
    pre_releases = [r for r in available_releases if r.is_pre_release]

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
        ui.label(f"New version{'s' if len(available_releases) > 1 else ''} available!").style(
            "color: #6E93D6; font-size: 200%; font-weight: 300"
        )

        if normal_releases:
            ui.label("Releases").classes("text-lg font-semibold mt-4")
            for r in normal_releases:
                with ui.row():
                    ui.label(f"Version {r.version}")
                    ui.link("View on GitHub", r.url, new_tab=True)
                with ui.expansion("Notes").classes("w-full"):
                    ui.markdown(normalize_markdown(r.notes))

        if pre_releases:
            ui.label("Pre-releases").classes("text-lg font-semibold mt-4")
            for r in pre_releases:
                with ui.row():
                    ui.label(f"Version {r.version} (pre-release)")
                    ui.link("View on GitHub", r.url, new_tab=True)
                with ui.expansion("Notes").classes("w-full"):
                    ui.markdown(normalize_markdown(r.notes))

        ui.button("Close", on_click=dialog.close)

    dialog.open()



