import asyncio
import json
import re
import tempfile
from functools import partial

from nicegui import ui
from nicegui.element import Element
from shapely.geometry import Point
from pyproj import Transformer

from apps.gui.helpers.km_service_manager import get_km_service

# RD Amersfoort <-> WGS84 transformers
rd2wgs = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)
wgs2rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True)


class MapCard:
    def __init__(self, center, zoom=15, on_map_click=None):
        self.zoom_lvl = zoom
        self.map = ui.leaflet(center=center, zoom=zoom).classes("w-full h-full flex-1")
        if on_map_click:
            self.map.on("map-click", on_map_click)
        self.marker = None
        self.geojson_layers = []

    def update_marker(self, lat, lon):
        if self.marker:
            self.map.remove_layer(self.marker)
        self.marker = self.map.marker(latlng=(lat, lon))

    def add_geojson(self, geojson: dict):
        self.clear_geojson()

        features = geojson["features"]
        if not features:
            return

        for feature in features:
            geom = feature["geometry"]
            coords = geom["coordinates"]

            if geom["type"] == "Point":
                latlng = (coords[1], coords[0])
                layer = self.map.generic_layer(
                    name="circle", args=[latlng, {"radius": 2, "color": "red"}]
                )
                self.map.set_center(latlng)
                self.map.set_zoom(self.zoom_lvl)

            elif geom["type"] == "LineString":
                latlngs = [(c[1], c[0]) for c in coords]
                layer = self.map.generic_layer(
                    name="polyline", args=[latlngs, {"color": "green"}]
                )
                self.map.set_center(latlngs[len(latlngs) // 2])
                self.map.set_zoom(self.zoom_lvl)

            elif geom["type"] == "Polygon":
                latlngs = [(c[1], c[0]) for c in coords[0]]
                layer = self.map.generic_layer(
                    name="polygon", args=[latlngs, {"color": "red", "fillOpacity": 0.5}]
                )
                self.map.set_center(latlngs[0])
                self.map.set_zoom(self.zoom_lvl)

            else:
                continue

            self.geojson_layers.append(layer)

    def clear_geojson(self):
        for layer in self.geojson_layers:
            self.map.remove_layer(layer)
        self.geojson_layers.clear()


class KmResponseCard:
    def __init__(
        self, index, km_measures, geojson, input_xy, on_download, on_close, on_go_to
    ):
        self.index = index
        self.km_measures = km_measures
        self.geojson = geojson
        self.input_xy = input_xy
        self.on_download = on_download
        self.on_close = on_close
        self.on_go_to = on_go_to
        self.name = f"Result #{self.index}"
        self.card = None
        self.map_card = None

    def build(self):
        self.card = ui.card().classes("p-2 shadow w-72 flex-none relative")
        with self.card:
            # ✅ Close button (right side)
            ui.button(icon="close", on_click=self.on_close).props(
                "flat round dense"
            ).classes("absolute top-1 right-1 z-10")

            # ✅ Aim icon to the LEFT of close, with small gap
            ui.button(icon="my_location", on_click=self.on_go_to).props(
                "flat round dense"
            ).classes("absolute top-1 right-10 z-10")

            with ui.column().classes("w-full gap-0"):
                self.name_input = ui.input(
                    label="Name",
                    value=self.name,
                    placeholder="Enter name...",
                    on_change=self.on_name_change,
                ).classes("w-full m-0 text-sm")

                if not self.km_measures:
                    ui.label("No KM values found.").classes("text-red-500 text-xs m-0")
                else:
                    for res in self.km_measures:
                        ui.label(f"{res.display}").classes("font-semibold text-xl m-0")
                ui.label(f"Input: {self.input_xy}").classes("text-xs text-gray-600 m-0")

            with ui.element("div").classes("w-full h-48"):
                # TODO: this should be the input so we do not zoom to groningen :)
                self.map_card = MapCard(center=[53.2107, 6.5636], zoom=15)
                self.map_card.add_geojson(self.geojson)

        return self.card

    def on_name_change(self):
        self.name = self.name_input.value


class KmTool:
    def __init__(self, container: Element):
        self.is_syncing = False
        self.use_wgs = False
        self.rd_point = Point(233592, 581094)
        self.result = None
        self.response_cards = []

        with container:
            with ui.row().classes("w-full flex flex-nowrap"):
                with ui.column().classes("w-1/3 p-4 flex-none"):
                    # ui.label("Enter Coordinates").classes("text-md font-bold")
                    self.km_label = ui.label("").classes(
                        "text-xl text-green-700 font-semibold p-o m-0"
                    )

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

                    ui.label("OR input coordinate pair").classes(
                        "text-sm italic text-gray-500"
                    )
                    self.xy_input = ui.input(
                        label="X,Y Pair", on_change=self.on_xystring_change
                    ).classes("w-full")

                    ui.label("OR input GML Point").classes(
                        "text-sm italic text-gray-500"
                    )
                    self.gml_input_rd = ui.input(
                        label="GML Coordinates", on_change=self.on_gml_change
                    ).classes("w-full")

                    self.mode_checkbox = ui.checkbox(
                        "Use WGS84 (lat/lon)",
                        value=False,
                        on_change=self.on_mode_change,
                    )

                with ui.column().classes("w-2/3 p-4 flex flex-col flex-1 h-full"):
                    self.input_map_card = MapCard(
                        center=[53.2107, 6.5636],
                        zoom=12,
                        on_map_click=self.on_map_click,
                    )

            with ui.row().classes("h-4"):
                ui.label("").props("inner-html")

            self.result_area = ui.row().classes(
                "mt-6 w-full flex-wrap content-start gap-4 overflow-auto max-h-[80vh]"
            )

        self.sync_all_fields(run_lookup=False)

    async def resolve_km_from_point(self, point: Point):
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

    def sync_all_fields(self, run_lookup=True):
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
        self.input_map_card.update_marker(lat, lon)

        # ✅ Clear KM value when syncing without lookup
        if not run_lookup:
            self.km_label.text = ""

        self.is_syncing = False

        if run_lookup:
            asyncio.create_task(self.run_km_lookup())

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
            match = re.search(
                r"<gml:coordinates>(.*?)</gml:coordinates>", self.gml_input_rd.value
            )
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
        self.input_map_card.map.set_center((lat, lon))
        self.rd_point = Point(rd_x, rd_y)
        self.sync_all_fields()

    async def download_geojson(self):
        if not self.result:
            ui.notify("No KM result to download.", type="warning")
            return

        geojson_string = self.result.geojson_string()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as tmp:
            tmp.write(geojson_string.encode("utf-8"))
            tmp_path = tmp.name

        ui.download(tmp_path, filename="point.geojson")

    def close_card(self, card):
        if card.card:
            card.card.delete()
        if card in self.response_cards:
            self.response_cards.remove(card)

    def go_to_result_point(self, point: Point):
        self.rd_point = point
        lon, lat = rd2wgs.transform(point.x, point.y)
        self.input_map_card.map.set_center((lat, lon))
        self.input_map_card.update_marker(lat, lon)
        self.sync_all_fields(run_lookup=False)

    async def run_km_lookup(self):
        try:
            self.result = await self.resolve_km_from_point(self.rd_point)
            geojson = json.loads(self.result.geojson_string())
            input_xy = self.format_point_xystring(self.rd_point)

            self.input_map_card.add_geojson(geojson)

            # ✅ Update live KM display
            if self.result and self.result.km_measures:
                self.km_label.text = f"KM: {self.result.km_measures[0].display}"
            else:
                self.km_label.text = "KM: -"

            def on_download():
                asyncio.create_task(self.download_geojson())

            card = KmResponseCard(
                index=len(self.response_cards) + 1,
                km_measures=self.result.km_measures,
                geojson=geojson,
                input_xy=input_xy,
                on_download=on_download,
                on_close=None,
                on_go_to=None,
            )

            card.on_close = partial(self.close_card, card)
            card.on_go_to = partial(self.go_to_result_point, self.rd_point)

            self.response_cards.append(card)

            with self.result_area:
                card.build()

        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")
