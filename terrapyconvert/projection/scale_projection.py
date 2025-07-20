"""
Scale projection transformation.
"""
from .projection_transform import ProjectionTransform
from .geographic_projection import GeographicProjection
from typing import List, Tuple
import math


class ScaleProjection(ProjectionTransform):
    """Projection that scales coordinates by specified factors."""
    
    def __init__(self, input_projection: GeographicProjection, scale_x: float, scale_y: float):
        super().__init__(input_projection)
        self.scale_x: float = scale_x
        self.scale_y: float = scale_y
    
    def to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Convert scaled coordinates back to geographic coordinates."""
        return self.input.to_geo(x / self.scale_x, y / self.scale_y)
    
    def from_geo(self, lon: float, lat: float) -> Tuple[float, float]:
        """Convert geographic coordinates to scaled coordinates."""
        x, y = self.input.from_geo(lon, lat)
        return x * self.scale_x, y * self.scale_y
    
    def upright(self) -> bool:
        """Check if projection is upright, accounting for y-scale sign."""
        return not self.input.upright() if self.scale_y < 0 else self.input.upright()
    
    def bounds(self) -> List[float]:
        """Get scaled bounds."""
        bounds = self.input.bounds()
        return [
            bounds[0] * self.scale_x,
            bounds[1] * self.scale_y,
            bounds[2] * self.scale_x,
            bounds[3] * self.scale_y
        ]
    
    def meters_per_unit(self) -> float:
        """Get adjusted meters per unit."""
        base_mpu = self.input.meters_per_unit()
        scale_factor = math.sqrt((self.scale_x * self.scale_x + self.scale_y * self.scale_y) / 2)
        return base_mpu / scale_factor
