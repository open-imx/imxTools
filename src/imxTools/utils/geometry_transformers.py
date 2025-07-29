from pyproj import Transformer

transform_rd2wgs = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)
transform_wgs2rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True)
