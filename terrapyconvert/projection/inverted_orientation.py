"""
Inverted orientation transformation.
"""
from .projection_transform import ProjectionTransform
from .geographic_projection import GeographicProjection
from typing import List, Tuple


class InvertedOrientation(ProjectionTransform):
    """Projection transform that swaps X and Y coordinates."""
    
    def __init__(self, input_projection: GeographicProjection):
        super().__init__(input_projection)
    
    def to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Convert coordinates back to geographic without swapping."""
        return self.input.to_geo(x, y)
    
    def from_geo(self, lon: float, lat: float) -> Tuple[float, float]:
        """Convert geographic coordinates, swapping X and Y in result."""
        x, y = self.input.from_geo(lon, lat)
        return y, x  # Swap coordinates
    
    def bounds(self) -> List[float]:
        """Get bounds with X and Y swapped."""
        bounds = self.input.bounds()
        return [bounds[1], bounds[0], bounds[3], bounds[2]]
