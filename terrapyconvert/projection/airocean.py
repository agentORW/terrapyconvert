"""
Airocean projection implementation.
"""
from .geographic_projection import GeographicProjection
from typing import List, Tuple
import math


class Airocean(GeographicProjection):
    """Airocean icosahedral projection."""
    
    # Constants
    ARC: float = 2 * math.asin(math.sqrt(5 - math.sqrt(5)) / math.sqrt(10))
    TO_RADIANS: float = math.pi / 180
    ROOT3: float = math.sqrt(3)
    
    # Icosahedron vertices (lon, lat pairs converted to radians in __init__)
    _VERT_RAW = [
        10.536199, 64.700000,
        -5.245390, 2.300882,
        58.157706, 10.447378,
        122.300000, 39.100000,
        -143.478490, 50.103201,
        -67.132330, 23.717925,
        36.521510, -50.103200,
        112.867673, -23.717930,
        174.754610, -2.300882,
        -121.842290, -10.447350,
        -57.700000, -39.100000,
        -169.463800, -64.700000,
    ]
    
    # Triangle face definitions (vertex indices)
    ISO = [
        2, 1, 6,    # 0
        1, 0, 2,    # 1
        0, 1, 5,    # 2
        1, 5, 10,   # 3
        1, 6, 10,   # 4
        7, 2, 6,    # 5
        2, 3, 7,    # 6
        3, 0, 2,    # 7
        0, 3, 4,    # 8
        4, 0, 5,    # 9 (Quebec)
        5, 4, 9,    # 10
        9, 5, 10,   # 11
        10, 9, 11,  # 12
        11, 6, 10,  # 13
        6, 7, 11,   # 14
        8, 3, 7,    # 15
        8, 3, 4,    # 16
        8, 4, 9,    # 17
        9, 8, 11,   # 18
        7, 8, 11,   # 19
        11, 6, 7,   # 20 (child of 14)
        3, 7, 8,    # 21 (child of 15)
    ]
    
    # 2D map centers
    CENTER_MAP_RAW = [
        -3, 7,   # 0
        -2, 5,   # 1
        -1, 7,   # 2
        2, 5,    # 3
        4, 5,    # 4
        -4, 1,   # 5
        -3, -1,  # 6
        -2, 1,   # 7
        -1, -1,  # 8
        0, 1,    # 9
        1, -1,   # 10
        2, 1,    # 11
        3, -1,   # 12
        4, 1,    # 13
        5, -1,   # 14 (left side, right to be cut)
        -3, -5,  # 15
        -1, -5,  # 16
        1, -5,   # 17
        2, -7,   # 18
        -4, -7,  # 19
        -5, -5,  # 20 (pseudo triangle, child of 14)
        -2, -7,  # 21 (pseudo triangle, child of 15)
    ]
    
    # Triangle flip flags
    FLIP_TRIANGLE = [
        1, 0, 1, 0, 0,
        1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
        1, 1, 1, 0, 0,
        1, 0,
    ]
    
    # Face grid for fast triangle lookup
    FACE_ON_GRID = [
        -1, -1, 0, 1, 2, -1, -1, 3, -1, 4, -1,
        -1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
        20, 19, 15, 21, 16, -1, 17, 18, -1, -1, -1,
    ]
    
    # Mathematical constants for triangle transform
    Z: float = math.sqrt(5 + 2 * math.sqrt(5)) / math.sqrt(15)
    EL: float = math.sqrt(8) / math.sqrt(5 + math.sqrt(5))
    EL6: float = EL / 6
    DVE: float = math.sqrt(3 + math.sqrt(5)) / math.sqrt(5 + math.sqrt(5))
    R: float = -3 * EL6 / DVE
    
    OUT_OF_BOUNDS = (float('nan'), float('nan'))
    
    def __init__(self):
        super().__init__()
        self.newton: int = 5
        
        # Initialize computed arrays
        self._initialize_vertices()
        self._initialize_centers()
        self._initialize_matrices()
    
    def _initialize_vertices(self):
        """Initialize vertex coordinates in radians."""
        self.VERT = []
        for i in range(0, len(self._VERT_RAW), 2):
            lon = self._VERT_RAW[i] * self.TO_RADIANS
            lat = (90 - self._VERT_RAW[i + 1]) * self.TO_RADIANS
            self.VERT.extend([lon, lat])
    
    def _initialize_centers(self):
        """Initialize 2D map centers."""
        self.CENTER_MAP = []
        for i in range(0, len(self.CENTER_MAP_RAW), 2):
            x = self.CENTER_MAP_RAW[i] * 0.5 * self.ARC
            y = self.CENTER_MAP_RAW[i + 1] * self.ARC * self.ROOT3 / 12
            self.CENTER_MAP.extend([x, y])
    
    def _initialize_matrices(self):
        """Initialize rotation matrices for each triangle face."""
        self.CENTROID = [0.0] * 66  # 22 faces * 3 coords
        self.ROTATION_MATRIX = [0.0] * 198  # 22 faces * 9 elements
        self.INVERSE_ROTATION_MATRIX = [0.0] * 198
        
        for i in range(22):
            # Get triangle vertices
            a = self._cart(self.VERT[2 * self.ISO[i * 3]], self.VERT[2 * self.ISO[i * 3] + 1])
            b = self._cart(self.VERT[2 * self.ISO[i * 3 + 1]], self.VERT[2 * self.ISO[i * 3 + 1] + 1])
            c = self._cart(self.VERT[2 * self.ISO[i * 3 + 2]], self.VERT[2 * self.ISO[i * 3 + 2] + 1])
            
            # Calculate centroid
            x_sum = a[0] + b[0] + c[0]
            y_sum = a[1] + b[1] + c[1]
            z_sum = a[2] + b[2] + c[2]
            
            mag = math.sqrt(x_sum * x_sum + y_sum * y_sum + z_sum * z_sum)
            
            self.CENTROID[3 * i] = x_sum / mag
            self.CENTROID[3 * i + 1] = y_sum / mag
            self.CENTROID[3 * i + 2] = z_sum / mag
            
            # Calculate rotation angles
            c_lon = math.atan2(y_sum, x_sum)
            c_lat = math.atan2(math.sqrt(x_sum * x_sum + y_sum * y_sum), z_sum)
            
            # Rotate first vertex to determine final rotation
            v = self._y_rot(self.VERT[2 * self.ISO[i * 3]] - c_lon, self.VERT[2 * self.ISO[i * 3] + 1], -c_lat)
            
            # Create rotation matrices
            self._produce_zyz_rotation_matrix(self.ROTATION_MATRIX, i * 9, -c_lon, -c_lat, (math.pi / 2) - v[0])
            self._produce_zyz_rotation_matrix(self.INVERSE_ROTATION_MATRIX, i * 9, v[0] - (math.pi / 2), c_lat, c_lon)
    
    @staticmethod
    def _cart(longitude: float, phi: float) -> Tuple[float, float, float]:
        """Convert spherical to cartesian coordinates."""
        sin_phi = math.sin(phi)
        return (sin_phi * math.cos(longitude), sin_phi * math.sin(longitude), math.cos(phi))
    
    def _y_rot(self, longitude: float, phi: float, rot: float) -> Tuple[float, float]:
        """Apply Y-axis rotation to spherical coordinates."""
        c = self._cart(longitude, phi)
        
        x = c[0]
        new_x = c[2] * math.sin(rot) + x * math.cos(rot)
        new_z = c[2] * math.cos(rot) - x * math.sin(rot)
        
        mag = math.sqrt(new_x * new_x + c[1] * c[1] + new_z * new_z)
        new_x /= mag
        c_y = c[1] / mag
        new_z /= mag
        
        return (
            math.atan2(c_y, new_x),
            math.atan2(math.sqrt(new_x * new_x + c_y * c_y), new_z)
        )
    
    @staticmethod
    def _produce_zyz_rotation_matrix(out: List[float], offset: int, a: float, b: float, c: float):
        """Produce ZYZ rotation matrix."""
        sin_a = math.sin(a)
        cos_a = math.cos(a)
        sin_b = math.sin(b)
        cos_b = math.cos(b)
        sin_c = math.sin(c)
        cos_c = math.cos(c)
        
        out[offset] = cos_a * cos_b * cos_c - sin_c * sin_a
        out[offset + 1] = -sin_a * cos_b * cos_c - sin_c * cos_a
        out[offset + 2] = cos_c * sin_b
        
        out[offset + 3] = sin_c * cos_b * cos_a + cos_c * sin_a
        out[offset + 4] = cos_c * cos_a - sin_c * cos_b * sin_a
        out[offset + 5] = sin_c * sin_b
        
        out[offset + 6] = -sin_b * cos_a
        out[offset + 7] = sin_b * sin_a
        out[offset + 8] = cos_b
    
    def _find_triangle(self, x: float, y: float, z: float) -> int:
        """Find the triangle face closest to the given 3D point."""
        min_dist = float('inf')
        face = 0
        
        for i in range(20):
            x_d = self.CENTROID[3 * i] - x
            y_d = self.CENTROID[3 * i + 1] - y
            z_d = self.CENTROID[3 * i + 2] - z
            
            dist_sq = x_d * x_d + y_d * y_d + z_d * z_d
            if dist_sq < min_dist:
                if dist_sq < 0.1:
                    return i
                face = i
                min_dist = dist_sq
        
        return face
    
    @classmethod
    def _find_triangle_grid(cls, x: float, y: float) -> int:
        """Find triangle face using grid lookup."""
        x_p = x / cls.ARC
        y_p = y / (cls.ARC * cls.ROOT3)
        
        if y_p > -0.25:
            if y_p < 0.25:  # middle
                row = 1
            elif y_p <= 0.75:  # top
                row = 0
                y_p = 0.5 - y_p  # translate to middle and flip
            else:
                return -1
        elif y_p >= -0.75:  # bottom
            row = 2
            y_p = -y_p - 0.5  # translate to middle and flip
        else:
            return -1
        
        y_p += 0.25  # change origin to vertex 4
        
        # rotate coords 45 degrees
        x_r = x_p - y_p
        y_r = x_p + y_p
        
        g_x = int(math.floor(x_r))
        g_y = int(math.floor(y_r))
        
        col = 2 * g_x + (0 if g_y == g_x else 1) + 6
        
        if col < 0 or col >= 11:
            return -1
        
        return cls.FACE_ON_GRID[row * 11 + col]
    
    def _triangle_transform(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """Transform 3D coordinates to 2D triangle coordinates."""
        s = self.Z / z
        
        x_p = s * x
        y_p = s * y
        
        a = math.atan((2 * y_p / self.ROOT3 - self.EL6) / self.DVE)
        b = math.atan((x_p - y_p / self.ROOT3 - self.EL6) / self.DVE)
        c = math.atan((-x_p - y_p / self.ROOT3 - self.EL6) / self.DVE)
        
        return (0.5 * (b - c), (2 * a - b - c) / (2 * self.ROOT3))
    
    def _inverse_triangle_transform_newton(self, x_pp: float, y_pp: float) -> Tuple[float, float, float]:
        """Inverse triangle transform using Newton's method."""
        tan_a_off = math.tan(self.ROOT3 * y_pp + x_pp)
        tan_b_off = math.tan(2 * x_pp)
        
        a_numer = tan_a_off * tan_a_off + 1
        b_numer = tan_b_off * tan_b_off + 1
        
        tan_a = tan_a_off
        tan_b = tan_b_off
        tan_c = 0.0
        
        a_denom = 1.0
        b_denom = 1.0
        
        for _ in range(self.newton):
            f = tan_a + tan_b + tan_c - self.R
            f_p = a_numer * a_denom * a_denom + b_numer * b_denom * b_denom + 1
            
            tan_c -= f / f_p
            
            a_denom = 1 / (1 - tan_c * tan_a_off)
            b_denom = 1 / (1 - tan_c * tan_b_off)
            
            tan_a = (tan_c + tan_a_off) * a_denom
            tan_b = (tan_c + tan_b_off) * b_denom
        
        y_p = self.ROOT3 * (self.DVE * tan_a + self.EL6) / 2
        x_p = self.DVE * tan_b + y_p / self.ROOT3 + self.EL6
        
        # Convert back to 3D coordinates
        x_p_over_z = x_p / self.Z
        y_p_over_z = y_p / self.Z
        
        z = 1 / math.sqrt(1 + x_p_over_z * x_p_over_z + y_p_over_z * y_p_over_z)
        
        return (z * x_p_over_z, z * y_p_over_z, z)
    
    def _inverse_triangle_transform(self, x: float, y: float) -> Tuple[float, float, float]:
        """Inverse triangle transform."""
        return self._inverse_triangle_transform_newton(x, y)
    
    def from_geo(self, lon: float, lat: float) -> Tuple[float, float]:
        """Convert geographic coordinates to projected coordinates."""
        lat = 90 - lat
        lon_rad = lon * self.TO_RADIANS
        lat_rad = lat * self.TO_RADIANS
        
        sin_phi = math.sin(lat_rad)
        
        x = math.cos(lon_rad) * sin_phi
        y = math.sin(lon_rad) * sin_phi
        z = math.cos(lat_rad)
        
        face = self._find_triangle(x, y, z)
        
        # Apply rotation matrix
        off = 9 * face
        x_p = (x * self.ROTATION_MATRIX[off] + 
               y * self.ROTATION_MATRIX[off + 1] + 
               z * self.ROTATION_MATRIX[off + 2])
        y_p = (x * self.ROTATION_MATRIX[off + 3] + 
               y * self.ROTATION_MATRIX[off + 4] + 
               z * self.ROTATION_MATRIX[off + 5])
        z_p = (x * self.ROTATION_MATRIX[off + 6] + 
               y * self.ROTATION_MATRIX[off + 7] + 
               z * self.ROTATION_MATRIX[off + 8])
        
        out_x, out_y = self._triangle_transform(x_p, y_p, z_p)
        
        # Apply flip if needed
        if self.FLIP_TRIANGLE[face] != 0:
            out_x = -out_x
            out_y = -out_y
        
        # Handle special face transformations
        orig_x = out_x
        if ((face == 15 and orig_x > out_y * self.ROOT3) or face == 14) and orig_x > 0:
            out_x = 0.5 * orig_x - 0.5 * self.ROOT3 * out_y
            out_y = 0.5 * self.ROOT3 * orig_x + 0.5 * out_y
            face += 6  # shift 14->20 & 15->21
        
        # Apply center offset
        out_x += self.CENTER_MAP[face * 2]
        out_y += self.CENTER_MAP[face * 2 + 1]
        
        return (out_x, out_y)
    
    def to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Convert projected coordinates to geographic coordinates."""
        face = self._find_triangle_grid(x, y)
        
        if face == -1:
            return self.OUT_OF_BOUNDS
        
        # Remove center offset
        x -= self.CENTER_MAP[face * 2]
        y -= self.CENTER_MAP[face * 2 + 1]
        
        # Check bounds for special faces
        if face == 14 and x > 0:
            return self.OUT_OF_BOUNDS
        elif face == 20 and -y * self.ROOT3 > x:
            return self.OUT_OF_BOUNDS
        elif face == 15 and x > 0 and x > y * self.ROOT3:
            return self.OUT_OF_BOUNDS
        elif face == 21 and (x < 0 or -y * self.ROOT3 > x):
            return self.OUT_OF_BOUNDS
        
        # Apply flip if needed
        if self.FLIP_TRIANGLE[face] != 0:
            x = -x
            y = -y
        
        # Inverse triangle transform
        x_3d, y_3d, z_3d = self._inverse_triangle_transform(x, y)
        
        # Apply inverse rotation matrix
        off = 9 * face
        x_p = (x_3d * self.INVERSE_ROTATION_MATRIX[off] + 
               y_3d * self.INVERSE_ROTATION_MATRIX[off + 1] + 
               z_3d * self.INVERSE_ROTATION_MATRIX[off + 2])
        y_p = (x_3d * self.INVERSE_ROTATION_MATRIX[off + 3] + 
               y_3d * self.INVERSE_ROTATION_MATRIX[off + 4] + 
               z_3d * self.INVERSE_ROTATION_MATRIX[off + 5])
        z_p = (x_3d * self.INVERSE_ROTATION_MATRIX[off + 6] + 
               y_3d * self.INVERSE_ROTATION_MATRIX[off + 7] + 
               z_3d * self.INVERSE_ROTATION_MATRIX[off + 8])
        
        # Convert to geographic coordinates
        lon = math.atan2(y_p, x_p) / self.TO_RADIANS
        lat = 90 - math.acos(z_p) / self.TO_RADIANS
        
        return (lat, lon)
