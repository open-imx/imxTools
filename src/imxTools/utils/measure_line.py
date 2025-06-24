from dataclasses import dataclass
from enum import Enum

import numpy as np
from imxInsights.utils.shapely.shapely_geojson import ShapelyGeoJsonFeature
from numpy._typing import NDArray
from shapely import LineString, Point

# TODO: this should be part of imxInsights


class ProjectionPointPosition(Enum):
    LEFT = "left"
    RIGHT = "right"
    ON_LINE = "on_line"
    UNDEFINED = "undefined"


class ProjectionsStatus(Enum):
    PERPENDICULAR = "perpendicular"
    ANGLE = "on_a_angle"
    OVERSHOOT = "overshoot"
    UNDERSHOOT = "undershoot"
    UNDEFINED = "undefined"


@dataclass
class PointMeasureResult:
    point_to_project: Point
    projection_line: LineString
    projected_point: Point
    measure_2d: float
    measure_3d: float | None
    side: ProjectionPointPosition
    overshoot_undershoot: ProjectionsStatus

    def __repr__(self) -> str:
        return (
            f"LineMeasureResult(point_to_project={self.point_to_project}, "
            f"projected_point={self.projected_point}, side={self.side}"
            f"measure_2d={self.measure_2d:.3f}, measure_3d={self.measure_3d}, "
            f"overshoot_undershoot={self.overshoot_undershoot.value})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def as_geojson_features(self):
        features = [
            ShapelyGeoJsonFeature([self.point_to_project], {"type": "input_point"}),
            ShapelyGeoJsonFeature([self.projection_line], {"type": "projection_line"}),
            ShapelyGeoJsonFeature(
                [self.projected_point],
                {
                    "type": "projected_point",
                    "measure_2d": self.measure_2d,
                    "measure_3d": self.measure_3d,
                    "side": self.side.value,
                    "projection_status": self.overshoot_undershoot.value,
                },
            ),
            ShapelyGeoJsonFeature(
                [LineString([self.point_to_project, self.projected_point])],
                {"type": "perpendicular_line"},
            ),
        ]
        return features


@dataclass
class LineMeasureResult:
    from_result: PointMeasureResult
    to_result: PointMeasureResult

    @property
    def from_measure_2d(self) -> float:
        return self.from_result.measure_2d

    @property
    def to_measure_2d(self) -> float:
        return self.to_result.measure_2d

    @property
    def from_measure_3d(self) -> float | None:
        return self.from_result.measure_3d

    @property
    def to_measure_3d(self) -> float | None:
        return self.to_result.measure_3d

    def __repr__(self) -> str:
        return (
            f"LineMeasureResult("
            f"from_measure=2D:{self.from_measure_2d:.3f}, 3D:{self.from_measure_3d}, "
            f"from_point={self.from_result.projected_point},"
            f"to_measure=2D:{self.to_measure_2d:.3f}, 3D:{self.to_measure_3d}, "
            f"to_point={self.to_result.projected_point},"
            f"status_from={self.from_result.overshoot_undershoot.value}, "
            f"status_to={self.to_result.overshoot_undershoot.value})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def as_geojson_features(self):
        features = (
            self.from_result.as_geojson_features()
            + self.to_result.as_geojson_features()
        )
        features.append(
            ShapelyGeoJsonFeature(
                [
                    LineString(
                        [
                            self.from_result.projected_point,
                            self.to_result.projected_point,
                        ]
                    )
                ],
                {"type": "projected_segment"},
            )
        )
        return features


class MeasureLine:
    def __init__(
        self, line: list[list[float]] | NDArray[np.float64] | LineString
    ) -> None:
        shapely_input_line, line_array, is_3d = self._process_input(line)

        self.shapely_line: LineString = shapely_input_line
        self._line_array: NDArray[np.float64] = line_array
        self.is_3d: bool = is_3d

        cum_lengths_2d, cum_lengths_3d = self._compute_cumulative_distance()

        self._cum_lengths_2d: NDArray[np.float64] = cum_lengths_2d
        self._cum_lengths_3d: NDArray[np.float64] | None = cum_lengths_3d

    @staticmethod
    def _process_input(line) -> tuple[LineString, NDArray[np.float64], bool]:
        if isinstance(line, LineString):
            shapely_input_line = line
            line_array = np.array(list(line.coords), dtype=float)
        else:
            shapely_input_line = LineString(line)
            line_array = np.asarray(line, dtype=float)

        # Validate input line dimensions (must be 2D array with 2 or 3 columns)
        if line_array.ndim != 2 or line_array.shape[1] not in (2, 3):
            raise ValueError(
                "Input line must be a 2D array with shape (N, 2) or (N, 3)."
            )

        # If the line has 2D points, convert them to 3D by adding z=0
        if line_array.shape[1] == 2:
            line_array = np.column_stack((line_array, np.zeros(line_array.shape[0])))
            is_3d = False
        else:
            is_3d = True

        return shapely_input_line, line_array, is_3d

    def _compute_cumulative_distance(
        self,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64] | None]:
        """Precompute cumulative 2D distances along the line"""
        # Extract 2D coordinates
        coords_2d = self._line_array[:, :2]
        # Calculate differences between consecutive points
        diffs_2d = np.diff(coords_2d, axis=0)
        # Calculate lengths of each segment
        seg_lengths_2d = np.linalg.norm(diffs_2d, axis=1)
        # Cumulative 2D lengths
        cum_lengths_2d: NDArray[np.float64] = np.concatenate(
            ([0], np.cumsum(seg_lengths_2d))
        )

        # Precompute cumulative 3D distances if the line is 3D
        cum_lengths_3d: NDArray[np.float64] | None = None
        if self.is_3d:
            # Calculate differences between consecutive 3D points
            diffs_3d = np.diff(self._line_array, axis=0)
            # Calculate lengths of each segment in 3D
            seg_lengths_3d = np.linalg.norm(diffs_3d, axis=1)
            # Cumulative 3D lengths
            cum_lengths_3d = np.concatenate(([0], np.cumsum(seg_lengths_3d)))

        return cum_lengths_2d, cum_lengths_3d

    def project(
        self, point: list[float] | NDArray[np.float64] | Point
    ) -> PointMeasureResult:
        point = self._validate_and_process_point(point)

        # Use shapely project as it haz tested perpendicular projection and interpolated z
        input_point_shapely_2d, proj_measure_shapely, proj_point_shapely = (
            self._shapely_projection(point)
        )

        seg_index, prev_point_3d, next_point_3d = self._get_segment_data(
            proj_measure_shapely
        )

        proj_point_3d = np.array(
            [proj_point_shapely.x, proj_point_shapely.y, proj_point_shapely.z]
        )
        measure_3d = self._get_3d_measure(proj_point_3d, prev_point_3d, seg_index)

        is_perpendicular = self._is_perpendicular_projection(input_point_shapely_2d)
        side_of_line = ProjectionPointPosition.UNDEFINED
        if is_perpendicular:
            side_of_line = self._determine_side(
                Point(point), Point(prev_point_3d[:2]), Point(next_point_3d[:2])
            )
            projection_angle = ProjectionsStatus.PERPENDICULAR
        elif proj_measure_shapely == 0:
            # if not perpendicular and 0 length we assume its undershooting the line
            projection_angle = ProjectionsStatus.UNDERSHOOT
        elif proj_measure_shapely == self.shapely_line.length:
            # if not perpendicular and length max we assume its overshooting the line
            projection_angle = ProjectionsStatus.OVERSHOOT
        else:
            # we cant reverse point by projecting on measure and offset!
            # TODO: calculate angle so we can use it to recreate input point
            side_of_line = self._determine_side(
                Point(point), Point(prev_point_3d[:2]), Point(next_point_3d[:2])
            )
            projection_angle = ProjectionsStatus.ANGLE

        shapely_projection = Point(proj_point_3d)

        # TODO: add distance to line in 2d and 3d
        return PointMeasureResult(
            point_to_project=Point(point),
            projection_line=self.shapely_line,
            projected_point=shapely_projection,
            measure_2d=proj_measure_shapely,
            measure_3d=measure_3d,
            side=side_of_line,
            overshoot_undershoot=projection_angle,
        )

    @staticmethod
    def _validate_and_process_point(
        point: Point | list[float] | np.ndarray,
    ) -> np.ndarray:
        if isinstance(point, Point):
            # If the point has only 2 coordinates, add z=0 to convert it to 3D
            point = np.array([point.x, point.y, point.z if point.has_z else 0.0])

        # Ensure point is a numpy array and flatten it to 1D
        point = np.array(point, dtype=float).flatten()

        # If the point has only 2 coordinates, add z=0 to convert it to 3D
        if point.shape[0] == 2:
            point = np.append(point, 0)
        elif point.shape[0] != 3:
            raise ValueError("Input point must have 2 or 3 coordinates (x, y, [z]).")
        return point

    def _shapely_projection(self, point: np.ndarray) -> tuple[Point, float, Point]:
        input_point_shapely_2d = Point(float(point[0]), float(point[1]))
        proj_measure_shapely = self.shapely_line.project(input_point_shapely_2d)
        proj_point_shapely = self.shapely_line.interpolate(proj_measure_shapely)
        return input_point_shapely_2d, proj_measure_shapely, proj_point_shapely

    def _get_segment_data(self, proj_measure_shapely: float):
        seg_index = (
            np.searchsorted(self._cum_lengths_2d, proj_measure_shapely, side="right")
            - 1
        )
        seg_index = min(max(seg_index, 0), len(self._cum_lengths_2d) - 2)  # type: ignore
        prev_point_3d = self._line_array[seg_index]
        next_point_3d = self._line_array[seg_index + 1]
        return seg_index, prev_point_3d, next_point_3d

    def _get_projected_z(
        self, seg_index, proj_measure_shapely, prev_point_3d, next_point_3d
    ):
        seg_length = (
            self._cum_lengths_2d[seg_index + 1] - self._cum_lengths_2d[seg_index]
        )
        interpolation_factor_t = (
            0.0
            if seg_length == 0
            else (proj_measure_shapely - self._cum_lengths_2d[seg_index]) / seg_length
        )
        proj_z = prev_point_3d[2] + interpolation_factor_t * (
            next_point_3d[2] - prev_point_3d[2]
        )
        return proj_z

    def _get_3d_measure(self, proj_point_3d, prev_point_3d, seg_index):
        measure_3d = None
        if self.is_3d:
            # Calculate 3D distance along the segment
            d_segment = np.linalg.norm(proj_point_3d - prev_point_3d)
            # Total 3D distance
            if self._cum_lengths_3d is not None:
                measure_3d = self._cum_lengths_3d[seg_index] + d_segment
        return measure_3d

    @staticmethod
    def _determine_side(
        point: Point, segment_start: Point, segment_end: Point
    ) -> ProjectionPointPosition:
        delta_x = segment_end.x - segment_start.x
        delta_y = segment_end.y - segment_start.y

        # Compute the cross product (2D determinant)
        cross = delta_x * (point.y - segment_start.y) - delta_y * (
            point.x - segment_start.x
        )

        if cross > 0:
            return ProjectionPointPosition.LEFT
        elif cross < 0:
            return ProjectionPointPosition.RIGHT
        else:
            return ProjectionPointPosition.ON_LINE

    def _is_perpendicular_projection(self, point: Point, tol: float = 1e-7) -> bool:
        # Project the point onto the line.
        proj_distance = self.shapely_line.project(point)
        proj_point = self.shapely_line.interpolate(proj_distance)

        # Identify the segment containing the projection.
        coords = list(self.shapely_line.coords)
        cum_distance = 0.0
        segment = None

        for i in range(len(coords) - 1):
            seg_start = coords[i]
            seg_end = coords[i + 1]
            seg_line = LineString([seg_start, seg_end])
            seg_length = seg_line.length
            if cum_distance <= proj_distance <= cum_distance + seg_length:
                segment = (seg_start, seg_end)
                break
            cum_distance += seg_length

        if segment is None:
            raise ValueError("Projection did not fall on any segment of the line.")

        # Compute the direction vector of the segment in 2D.
        seg_start, seg_end = segment
        seg_start_2d = np.array(seg_start)[:2]
        seg_end_2d = np.array(seg_end)[:2]
        seg_vec_2d = seg_end_2d - seg_start_2d

        norm_seg = np.linalg.norm(seg_vec_2d)
        if norm_seg == 0:
            raise ValueError("Encountered a segment with zero length.")
        seg_unit = seg_vec_2d / norm_seg

        # Compute the vector from the projected point to the original point in 2D.
        pt_coords_2d = np.array(point.coords[0])[:2]
        proj_coords_2d = np.array(proj_point.coords[0])[:2]
        pt_vec = pt_coords_2d - proj_coords_2d

        # Check for orthogonality using the dot product.
        dot_product = np.dot(seg_unit, pt_vec)
        return abs(dot_product) < tol

    def project_line(self, input_line: LineString) -> LineMeasureResult:
        """
        Projects each vertex of a LineString onto the MeasureLine and returns a
        LineMeasureResult based on the points with the minimum and maximum 2D measure.
        """

        # TODO: we should handle all so list or npArray of coordinates

        if not isinstance(input_line, LineString):
            raise TypeError("Expected a shapely LineString as input.")

        if len(input_line.coords) < 2:
            raise ValueError("Input LineString must have at least 2 coordinates.")

        projected_results = [self.project(Point(coord)) for coord in input_line.coords]

        # Find min and max measure_2d
        from_result = projected_results[0]
        to_result = projected_results[-1]

        if from_result is None or to_result is None:
            raise ValueError(
                "Projection failed: measure_3d is None for one or more points."
            )

        return LineMeasureResult(from_result=from_result, to_result=to_result)
