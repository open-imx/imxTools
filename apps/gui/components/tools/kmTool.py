import asyncio
import json
import re
import tempfile

from nicegui import ui
from nicegui.element import Element
from shapely.geometry import Point
from pyproj import Transformer

from apps.gui.helpers.km_service_manager import get_km_service

# Use RD Amersfoort (EPSG:28992) <-> WGS84 (EPSG:4326)
rd2wgs = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)
wgs2rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True)


class KmTool:
    def __init__(self, container: Element):
        self.is_syncing = False
        self.use_wgs = False
        self.rd_point = Point(233592, 581094)
        self.result = None

        with container:
            with ui.row().classes("w-full flex flex-nowrap"):
                with ui.column().classes("w-1/3 p-4 flex-none"):
                    ui.label("Enter Coordinates").classes("text-md font-bold")

                    with ui.row():
                        self.x_input = ui.number(
                            label="X / Lon",
                            on_change=self.on_xy_change,
                            step=0.0001,
                        )

                        self.y_input = ui.number(
                            label="Y / Lat",
                            on_change=self.on_xy_change,
                            step=0.0001,
                        )

                    ui.label("OR input coordinate pair").classes("text-sm italic text-gray-500")
                    self.xy_input = ui.input(
                        label="X,Y Pair", on_change=self.on_xystring_change
                    ).classes("w-full")

                    ui.label("OR input GML Point").classes("text-sm italic text-gray-500")
                    self.gml_input_rd = ui.input(
                        label="GML Coordinates", on_change=self.on_gml_change
                    ).classes("w-full")

                    self.mode_checkbox = ui.checkbox(
                        "Use WGS84 (lat/lon)",
                        value=False,
                        on_change=self.on_mode_change
                    )

                with ui.column().classes("w-2/3 p-4 flex flex-col flex-1 h-full"):
                    self.map = ui.leaflet(center=[53.2107, 6.5636], zoom=8).classes("w-full flex-1")
                    self.map.on('map-click', self.on_map_click)
                    self.marker = None

            self.result_area = ui.column().classes("mt-6 w-full")
            with self.result_area:
                self.result_card = ui.card().classes("p-4 shadow-md w-full mb-2")
                with self.result_card:
                    self.result_content = ui.column().classes("w-full")

        self.sync_all_fields()

    async def resolve_km_from_point(self, point: Point):
        """Resolve KM measures from the KM service"""
        return get_km_service().get_km(point.x, point.y)

    def parse_decimal(self, value: str) -> float:
        return float(value.strip().replace(",", "."))

    def format_point_xystring(self, point: Point) -> str:
        return f"{point.x:.3f},{point.y:.3f}"

    def format_point_gml(self, point: Point) -> str:
        if self.use_wgs:
            lon, lat = rd2wgs.transform(point.x, point.y)
            return f"<gml:coordinates>{lon:.6f},{lat:.6f}</gml:coordinates>"
        else:
            return f"<gml:coordinates>{point.x:.3f},{point.y:.3f}</gml:coordinates>"

    def sync_all_fields(self):
        """Update ALL input fields & map using self.rd_point"""
        self.is_syncing = True

        rd_point = self.rd_point
        if self.use_wgs:
            lon, lat = rd2wgs.transform(rd_point.x, rd_point.y)
            display_point = Point(lon, lat)
        else:
            display_point = rd_point

        self.x_input.value = display_point.x
        self.y_input.value = display_point.y
        self.xy_input.value = self.format_point_xystring(display_point)
        self.gml_input_rd.value = self.format_point_gml(rd_point)

        lon, lat = rd2wgs.transform(rd_point.x, rd_point.y)
        self.update_map_marker(lat, lon)

        self.is_syncing = False

        asyncio.create_task(self.run_km_lookup())

    def update_map_marker(self, lat, lon):
        if self.marker:
            self.map.remove_layer(self.marker)
        self.marker = self.map.marker(latlng=(lat, lon))

    def on_mode_change(self):
        self.use_wgs = self.mode_checkbox.value
        self.sync_all_fields()

    def on_xy_change(self):
        if self.is_syncing:
            return
        try:
            x = self.x_input.value
            y = self.y_input.value
            if x is None or y is None:
                return
            if self.use_wgs:
                rd_x, rd_y = wgs2rd.transform(x, y)
            else:
                rd_x, rd_y = x, y
            self.rd_point = Point(rd_x, rd_y)
            self.sync_all_fields()
        except Exception as e:
            print(f"Error parsing XY input: {e}")

    def on_xystring_change(self):
        if self.is_syncing:
            return
        try:
            x_str, y_str = self.xy_input.value.strip().split(",")
            x = self.parse_decimal(x_str)
            y = self.parse_decimal(y_str)
            if self.use_wgs:
                rd_x, rd_y = wgs2rd.transform(x, y)
            else:
                rd_x, rd_y = x, y
            self.rd_point = Point(rd_x, rd_y)
            self.sync_all_fields()
        except Exception as e:
            print(f"Error parsing XY string: {e}")

    def on_gml_change(self):
        if self.is_syncing:
            return
        try:
            match = re.search(r"<gml:coordinates>(.*?)</gml:coordinates>", self.gml_input_rd.value)
            if match:
                coords = match.group(1).strip().split(",")
                x = self.parse_decimal(coords[0])
                y = self.parse_decimal(coords[1])
                if self.use_wgs:
                    rd_x, rd_y = wgs2rd.transform(x, y)
                else:
                    rd_x, rd_y = x, y
                self.rd_point = Point(rd_x, rd_y)
                self.sync_all_fields()
        except Exception as e:
            print(f"Error parsing GML input: {e}")

    async def on_map_click(self, event):
        if self.is_syncing:
            return
        lat = event.args["latlng"]["lat"]
        lon = event.args["latlng"]["lng"]
        rd_x, rd_y = wgs2rd.transform(lon, lat)
        self.rd_point = Point(rd_x, rd_y)
        self.sync_all_fields()

    async def download_geojson(self):
        """Download GeoJSON using self.result.geojson_string()"""
        if not self.result:
            ui.notify("No KM result to download.", type="warning")
            return

        geojson_string = self.result.geojson_string()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.geojson') as tmp:
            tmp.write(geojson_string.encode('utf-8'))
            tmp_path = tmp.name

        ui.download(tmp_path, filename="point.geojson")

    async def run_km_lookup(self):
        """Fetch KM measures and update result"""
        self.result_content.clear()
        try:
            self.result = await self.resolve_km_from_point(self.rd_point)
            if not self.result.km_measures:
                with self.result_content:
                    ui.label("No KM values found.").classes("text-red-500")
            else:
                with self.result_content:
                    for res in self.result.km_measures:
                        ui.label(f"{res.display}").classes("font-bold text-lg")

                    ui.button(
                        "Download GeoJSON",
                        on_click=self.download_geojson,
                    ).classes("mt-4 btn-primary")

                    ui.notify("KM values resolved!", type="positive")  # ✅ inside WITH
        except Exception as e:
            with self.result_content:
                ui.notify(f"Error: {e}", type="negative")
