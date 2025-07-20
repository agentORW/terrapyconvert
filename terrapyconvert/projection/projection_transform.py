"""
Base class for projection transforms.
"""
from .geographic_projection import GeographicProjection
from typing import List, Tuple


class ProjectionTransform(GeographicProjection):
    """Abstract base class for projection transformations."""
    
    def __init__(self, input_projection: GeographicProjection):
        self.input = input_projection
    
    def upright(self) -> bool:
        """Check if the underlying projection is upright."""
        return self.input.upright()
    
    def bounds(self) -> List[float]:
        """Get bounds from the underlying projection."""
        return self.input.bounds()
    
    def meters_per_unit(self) -> float:
        """Get meters per unit from the underlying projection."""
        return self.input.meters_per_unit()
