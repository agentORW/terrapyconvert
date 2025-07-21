"""
Conformal estimate projection.
"""
from .airocean import Airocean
from ..utils.invertable_vector_field import InvertableVectorField
from ..data.conformal import get_conformal_json
from typing import Tuple
import math


class ConformalEstimate(Airocean):
    """Conformal correction applied to Airocean projection."""
    
    VECTOR_SCALE_FACTOR: float = 1 / 1.1473979730192934
    
    def __init__(self):
        super().__init__()
        
        side_length = 256
        
        # Initialize arrays for conformal data
        xs = []
        ys = []
        
        for u in range(side_length + 1):
            px = [0.0] * (side_length + 1 - u)
            py = [0.0] * (side_length + 1 - u)
            xs.append(px)
            ys.append(py)
        
        # Load conformal data
        conformal_data = get_conformal_json()
        
        # Fill arrays with conformal data
        counter = 0
        for v in range(side_length + 1):
            for u in range(side_length + 1 - v):
                if counter < len(conformal_data):
                    entry = conformal_data[counter]
                    xs[u][v] = entry[0] * self.VECTOR_SCALE_FACTOR
                    ys[u][v] = entry[1] * self.VECTOR_SCALE_FACTOR
                else:
                    # Fallback to identity if data is insufficient
                    xs[u][v] = u / side_length * self.VECTOR_SCALE_FACTOR
                    ys[u][v] = v / side_length * self.VECTOR_SCALE_FACTOR
                counter += 1
        
        self.inverse = InvertableVectorField(xs, ys)
    
    def _triangle_transform(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """Apply conformal correction to triangle transform."""
        c = list(super()._triangle_transform(x, y, z))
        
        orig_x = c[0]
        orig_y = c[1]
        
        # Normalize to unit triangle
        c[0] /= self.ARC
        c[1] /= self.ARC
        
        # Apply correction
        c[0] += 0.5
        c[1] += self.ROOT3 / 6
        
        # Apply Newton's method for conformal correction
        corrected = self.inverse.apply_newtons_method(orig_x, orig_y, c[0], c[1], 5)
        
        c[0] = corrected[0] - 0.5
        c[1] = corrected[1] - self.ROOT3 / 6
        
        # Scale back
        c[0] *= self.ARC
        c[1] *= self.ARC
        
        return (c[0], c[1])
    
    def _inverse_triangle_transform(self, x: float, y: float) -> Tuple[float, float, float]:
        """Apply inverse conformal correction."""
        # Normalize
        x /= self.ARC
        y /= self.ARC
        
        # Apply offset
        x += 0.5
        y += self.ROOT3 / 6
        
        # Get conformal correction
        corrected = self.inverse.get_interpolated_vector(x, y)
        
        # Apply the correction and return to parent method
        return super()._inverse_triangle_transform(corrected[0], corrected[1])
    
    def meters_per_unit(self) -> float:
        """Get adjusted meters per unit accounting for conformal scaling."""
        return (40075017 / (2 * math.pi)) / self.VECTOR_SCALE_FACTOR
