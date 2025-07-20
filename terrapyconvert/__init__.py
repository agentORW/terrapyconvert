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

__version__ = "1.0.0"
__author__ = "Python Port"

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
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        Tuple of (x, z) Minecraft coordinates
    """
    x, z = _scale_proj.from_geo(lon, lat)
    return x, z


def from_geo_object(lat: float, lon: float) -> Dict[str, float]:
    """
    Convert real life coordinates to in-game coordinates, returns a dict.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        Dictionary with 'x' and 'z' Minecraft coordinates
    """
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
    """
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
    """
    lat, lon = _scale_proj.to_geo(x, z)
    return {"lat": lat, "lon": lon}


__all__ = [
    'from_geo',
    'from_geo_object', 
    'to_geo',
    'to_geo_object',
]
