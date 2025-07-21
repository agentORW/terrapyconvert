"""
Enumeration for projection orientations.
"""
from enum import Enum


class Orientation(Enum):
    """Orientation options for projections."""
    NONE = "none"
    UPRIGHT = "upright" 
    SWAPPED = "swapped"
