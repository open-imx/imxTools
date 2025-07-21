from enum import Enum


class MeasureAnalyseColumns(Enum):
    object_path = "Full object path in IMX structure"
    object_puic = "PUIC (unique identifier) of the object"
    object_name = "Human-readable name of the object"
    ref_field = "Field used to reference the rail connection"
    ref_field_value = "PUIC of the referenced rail connection"
    ref_field_name = "Name of the referenced rail connection"
    measure_type = "Measure type at, from or to measure"
    imx_measure = "Original atMeasure value from IMX data"
    calculated_measure_3d = "Calculated 3D measure along the rail geometry"
    abs_imx_vs_3d = "Absolute difference between IMX and calculated 3D measure"
    calculated_measure_2d = "Calculated 2D projected distance along the rail geometry"
    abs_imx_vs_2d = "Absolute difference between IMX and calculated 2D distance"
