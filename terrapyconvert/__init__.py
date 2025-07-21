"""
TerrapyConvert: Python library for converting geographic coordinates to Minecraft coordinates.

This library provides functions to convert between real-world latitude/longitude coordinates
and Minecraft BuildTheEarth (BTE) project coordinates.
"""
from typing import Tuple, Dict

from .projection import (
    ModifiedAirocean,
    ScaleProjection,
    Orientation,
    UprightOrientation,
    InvertedOrientation,
)

__version__ = "1.0.1"
__author__ = "Python Port"


def _validate_geographic_coordinates(lat: float, lon: float) -> None:
    """Validate geographic coordinates."""
    if not (-90 <= lat <= 90):
        raise ValueError(f'Invalid latitude: {lat} (must be between -90 and 90 degrees)')
    if not (-180 <= lon <= 180):
        raise ValueError(f'Invalid longitude: {lon} (must be between -180 and 180 degrees)')


def _validate_minecraft_coordinates(x: float, z: float) -> None:
    """Validate Minecraft coordinates - basic sanity checks."""
    # Based on comprehensive coordinate bounds from the BuildTheEarth projection:
    # X range: -20,933,914 to 23,382,239 blocks  
    # Z range: -13,876,057 to 12,077,397 blocks
    # Adding buffer for floating point precision and edge cases
    max_x = 25000000
    min_x = -25000000
    max_z = 15000000
    min_z = -15000000
    
    if not (min_x <= x <= max_x):
        raise ValueError(f'Invalid x coordinate: {x} (must be between {min_x} and {max_x})')
    if not (min_z <= z <= max_z):
        raise ValueError(f'Invalid z coordinate: {z} (must be between {min_z} and {max_z})')

# Initialize the projection chain
def _orient_projection(base, orientation: Orientation):
    """Apply orientation transformation to projection."""
    if base.upright():
        if orientation == Orientation.UPRIGHT:
            return base
        base = UprightOrientation(base)
    
    if orientation == Orientation.SWAPPED:
        return InvertedOrientation(base)
    elif orientation == Orientation.UPRIGHT:
        base = UprightOrientation(base)
    
    return base

# Create the projection pipeline
_projection = ModifiedAirocean()
_upright_proj = _orient_projection(_projection, Orientation.UPRIGHT)  
_scale_proj = ScaleProjection(_upright_proj, 7318261.522857145, 7318261.522857145)


def from_geo(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert real life coordinates to in-game coordinates.
    
    Args:
        lat: Latitude in degrees (must be between -90 and 90)
        lon: Longitude in degrees (must be between -180 and 180)
        
    Returns:
        Tuple of (x, z) Minecraft coordinates
        
    Raises:
        ValueError: If latitude or longitude are outside valid ranges
    """
    _validate_geographic_coordinates(lat, lon)
    x, z = _scale_proj.from_geo(lon, lat)
    return x, z


def from_geo_object(lat: float, lon: float) -> Dict[str, float]:
    """
    Convert real life coordinates to in-game coordinates, returns a dict.
    
    Args:
        lat: Latitude in degrees (must be between -90 and 90)
        lon: Longitude in degrees (must be between -180 and 180)
        
    Returns:
        Dictionary with 'x' and 'z' Minecraft coordinates
        
    Raises:
        ValueError: If latitude or longitude are outside valid ranges
    """
    _validate_geographic_coordinates(lat, lon)
    x, z = _scale_proj.from_geo(lon, lat)
    return {"x": x, "z": z}


def to_geo(x: float, z: float) -> Tuple[float, float]:
    """
    Convert in-game coordinates to real life coordinates.
    
    Args:
        x: Minecraft x coordinate
        z: Minecraft z coordinate
        
    Returns:
        Tuple of (latitude, longitude) in degrees
        
    Raises:
        ValueError: If coordinates are outside reasonable bounds
    """
    _validate_minecraft_coordinates(x, z)
    lat, lon = _scale_proj.to_geo(x, z)
    return lat, lon


def to_geo_object(x: float, z: float) -> Dict[str, float]:
    """
    Convert in-game coordinates to real life coordinates, returns a dict.
    
    Args:
        x: Minecraft x coordinate
        z: Minecraft z coordinate
        
    Returns:
        Dictionary with 'lat' and 'lon' coordinates in degrees
        
    Raises:
        ValueError: If coordinates are outside reasonable bounds
    """
    _validate_minecraft_coordinates(x, z)
    lat, lon = _scale_proj.to_geo(x, z)
    return {"lat": lat, "lon": lon}


__all__ = [
    'from_geo',
    'from_geo_object', 
    'to_geo',
    'to_geo_object',
]
