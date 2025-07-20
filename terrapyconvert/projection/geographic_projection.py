"""
Base geographic projection class for coordinate transformations.
"""
from abc import ABC, abstractmethod
from typing import Tuple, List


class GeographicProjection(ABC):
    """Abstract base class for geographic projections."""
    
    EARTH_CIRCUMFERENCE: float = 40075017.0
    EARTH_POLAR_CIRCUMFERENCE: float = 40008000.0
    
    def to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Convert projected coordinates to geographic coordinates."""
        return x, y
    
    def from_geo(self, lon: float, lat: float) -> Tuple[float, float]:
        """Convert geographic coordinates to projected coordinates."""
        return lon, lat
    
    def meters_per_unit(self) -> float:
        """Get meters per unit for this projection."""
        return 100000.0
    
    def bounds(self) -> List[float]:
        """Get the bounds of this projection [min_x, min_y, max_x, max_y]."""
        # Get bounds using extreme coordinates
        coords = [
            self.from_geo(-180, 0)[0],  # min_x candidate
            self.from_geo(0, -90)[1],   # min_y candidate  
            self.from_geo(180, 0)[0],   # max_x candidate
            self.from_geo(0, 90)[1],    # max_y candidate
        ]
        
        # Ensure proper ordering
        if coords[0] > coords[2]:
            coords[0], coords[2] = coords[2], coords[0]
            
        if coords[1] > coords[3]:
            coords[1], coords[3] = coords[3], coords[1]
            
        return coords
    
    def upright(self) -> bool:
        """Check if projection is upright (north pole y <= south pole y)."""
        north_y = self.from_geo(0, 90)[1]
        south_y = self.from_geo(0, -90)[1]
        return north_y <= south_y
