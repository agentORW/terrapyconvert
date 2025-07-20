"""
Invertable vector field for conformal corrections.
"""
from typing import List, Tuple
import math


class InvertableVectorField:
    """A vector field that can be inverted using Newton's method."""
    
    ROOT3: float = math.sqrt(3)
    
    def __init__(self, vector_x: List[List[float]], vector_y: List[List[float]]):
        self.side_length: int = len(vector_x) - 1
        self.vector_x = vector_x
        self.vector_y = vector_y
    
    def get_interpolated_vector(self, x: float, y: float) -> Tuple[float, float, float, float, float, float]:
        """Get interpolated vector and derivatives at given coordinates."""
        # Scale up triangle to be side_length across
        x *= self.side_length
        y *= self.side_length
        
        # Convert to triangle units
        v = 2 * y / self.ROOT3
        u = x - v * 0.5
        
        # Clamp to valid ranges
        u1 = max(0, min(int(u), self.side_length - 1))
        v1 = max(0, min(int(v), self.side_length - u1 - 1))
        
        # Determine which triangle we're in and get values
        flip = 1
        
        if y < -self.ROOT3 * (x - u1 - v1 - 1) or v1 == self.side_length - u1 - 1:
            # Lower triangle
            valx1 = self.vector_x[u1][v1]
            valy1 = self.vector_y[u1][v1]
            valx2 = self.vector_x[u1][v1 + 1]
            valy2 = self.vector_y[u1][v1 + 1]
            valx3 = self.vector_x[u1 + 1][v1]
            valy3 = self.vector_y[u1 + 1][v1]
            
            y3 = 0.5 * self.ROOT3 * v1
            x3 = (u1 + 1) + 0.5 * v1
        else:
            # Upper triangle
            valx1 = self.vector_x[u1][v1 + 1]
            valy1 = self.vector_y[u1][v1 + 1]
            valx2 = self.vector_x[u1 + 1][v1]
            valy2 = self.vector_y[u1 + 1][v1]
            valx3 = self.vector_x[u1 + 1][v1 + 1]
            valy3 = self.vector_y[u1 + 1][v1 + 1]
            
            flip = -1
            y = -y
            
            y3 = -(0.5 * self.ROOT3 * (v1 + 1))
            x3 = (u1 + 1) + 0.5 * (v1 + 1)
        
        # Calculate barycentric coordinates
        w1 = -(y - y3) / self.ROOT3 - (x - x3)
        w2 = 2 * (y - y3) / self.ROOT3
        w3 = 1 - w1 - w2
        
        # Interpolated values and derivatives
        val_x = valx1 * w1 + valx2 * w2 + valx3 * w3
        val_y = valy1 * w1 + valy2 * w2 + valy3 * w3
        
        dfdx = (valx3 - valx1) * self.side_length
        dfdy = self.side_length * flip * (2 * valx2 - valx1 - valx3) / self.ROOT3
        dgdx = (valy3 - valy1) * self.side_length
        dgdy = self.side_length * flip * (2 * valy2 - valy1 - valy3) / self.ROOT3
        
        return val_x, val_y, dfdx, dfdy, dgdx, dgdy
    
    def apply_newtons_method(self, expected_f: float, expected_g: float, 
                           x_est: float, y_est: float, iterations: int) -> Tuple[float, float]:
        """Apply Newton's method to find inverse mapping."""
        for _ in range(iterations):
            val_x, val_y, dfdx, dfdy, dgdx, dgdy = self.get_interpolated_vector(x_est, y_est)
            
            f = val_x - expected_f
            g = val_y - expected_g
            
            # Calculate determinant for matrix inversion
            determinant = 1.0 / (dfdx * dgdy - dfdy * dgdx)
            
            # Update estimates using Newton's method
            x_est -= determinant * (dgdy * f - dfdy * g)
            y_est -= determinant * (-dgdx * f + dfdx * g)
        
        return x_est, y_est
