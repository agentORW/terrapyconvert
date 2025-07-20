"""
Modified Airocean projection with custom transformations.
"""
from .conformal_estimate import ConformalEstimate
from .airocean import Airocean
from typing import Tuple, List
import math


class ModifiedAirocean(ConformalEstimate):
    """Modified Airocean projection with Eurasian adjustments."""
    
    THETA: float = -150 * Airocean.TO_RADIANS
    SIN_THETA: float = math.sin(THETA)
    COS_THETA: float = math.cos(THETA)
    
    # Bering strait and boundary constants
    BERING_X: float = -0.3420420960118339
    BERING_Y: float = -0.322211064085279
    ARCTIC_Y: float = -0.2
    
    ALEUTIAN_Y: float = -0.5000446805492526
    ALEUTIAN_XL: float = -0.5149231279757507
    ALEUTIAN_XR: float = -0.45
    
    def __init__(self):
        super().__init__()
        
        # Calculate derived constants
        self.ARCTIC_M = ((self.ARCTIC_Y - self.ROOT3 * self.ARC / 4) / 
                        (self.BERING_X - (-0.5 * self.ARC)))
        self.ARCTIC_B = self.ARCTIC_Y - self.ARCTIC_M * self.BERING_X
        
        self.ALEUTIAN_M = ((self.BERING_Y - self.ALEUTIAN_Y) / 
                          (self.BERING_X - self.ALEUTIAN_XR))
        self.ALEUTIAN_B = self.BERING_Y - self.ALEUTIAN_M * self.BERING_X
    
    def _is_eurasian_part(self, x: float, y: float) -> bool:
        """Determine if coordinates are in the Eurasian part."""
        if x > 0:
            return False
        if x < -0.5 * self.ARC:
            return True
        
        if y > self.ROOT3 * self.ARC / 4:  # above arctic ocean
            return x < 0
        
        if y < self.ALEUTIAN_Y:  # below bering sea
            return y < (self.ALEUTIAN_Y + self.ALEUTIAN_XL) - x
        
        if y > self.BERING_Y:  # boundary across arctic ocean
            if y < self.ARCTIC_Y:  # in strait
                return x < self.BERING_X
            # above strait
            return y < self.ARCTIC_M * x + self.ARCTIC_B
        
        return y > self.ALEUTIAN_M * x + self.ALEUTIAN_B
    
    def from_geo(self, lon: float, lat: float) -> Tuple[float, float]:
        """Convert geographic coordinates with Eurasian modifications."""
        c = list(super().from_geo(lon, lat))
        x, y = c[0], c[1]
        
        easia = self._is_eurasian_part(x, y)
        
        y -= 0.75 * self.ARC * self.ROOT3
        
        if easia:
            x += self.ARC
            
            # Apply rotation
            t = x
            x = self.COS_THETA * x - self.SIN_THETA * y
            y = self.SIN_THETA * t + self.COS_THETA * y
        else:
            x -= self.ARC
        
        # Swap coordinates
        c[0] = y
        c[1] = -x
        
        return (c[0], c[1])
    
    def to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Convert to geographic coordinates with Eurasian modifications."""
        # Determine if this is Eurasian part based on position
        if y < 0:
            easia = x > 0
        elif y > self.ARC / 2:
            easia = x > -self.ROOT3 * self.ARC / 2
        else:
            easia = y * -self.ROOT3 < x
        
        # Unswap coordinates
        t = x
        x = -y
        y = t
        
        if easia:
            # Apply inverse rotation
            t = x
            x = self.COS_THETA * x + self.SIN_THETA * y
            y = self.COS_THETA * y - self.SIN_THETA * t
            x -= self.ARC
        else:
            x += self.ARC
        
        y += 0.75 * self.ARC * self.ROOT3
        
        # Check if still in right part
        if easia != self._is_eurasian_part(x, y):
            return Airocean.OUT_OF_BOUNDS
        
        return super().to_geo(x, y)
    
    def bounds(self) -> List[float]:
        """Get bounds for the modified projection."""
        return [
            -1.5 * self.ARC * self.ROOT3,
            -1.5 * self.ARC,
            3 * self.ARC,
            self.ROOT3 * self.ARC
        ]
