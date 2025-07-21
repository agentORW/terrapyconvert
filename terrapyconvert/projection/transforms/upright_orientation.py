"""
Upright orientation transformation.
"""
from ..base.projection_transform import ProjectionTransform
from ..base.geographic_projection import GeographicProjection
from typing import List, Tuple


class UprightOrientation(ProjectionTransform):
    """Projection transform that flips the Y axis to make projection upright."""
    
    def __init__(self, input_projection: GeographicProjection):
        super().__init__(input_projection)
    
    def to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Convert coordinates back to geographic, flipping Y."""
        return self.input.to_geo(x, -y)
    
    def from_geo(self, lon: float, lat: float) -> Tuple[float, float]:
        """Convert geographic coordinates, flipping Y in result."""
        x, y = self.input.from_geo(lon, lat)
        return x, -y
    
    def upright(self) -> bool:
        """Returns opposite of input projection's upright status."""
        return not self.input.upright()
    
    def bounds(self) -> List[float]:
        """Get bounds with Y coordinates flipped."""
        bounds = self.input.bounds()
        return [bounds[0], -bounds[3], bounds[2], -bounds[1]]
