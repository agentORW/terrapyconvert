# TerrapyConvert

A Python package for converting geographic coordinates to Minecraft coordinates and vice versa for the BuildTheEarth (BTE) project.

This is a Python port of the TypeScript [terraconvert](https://github.com/Nachwahl/terraconvert/tree/9285b5f3d50b3cf0718b7a0e8e29b8eab1eb9163) package, designed to provide clean, pythonic APIs for coordinate conversion.

Install with pip: https://pypi.org/project/terrapyconvert/

## Installation

```bash
pip install terrapyconvert
```

## Usage

```python
from terrapyconvert import from_geo, to_geo

# Convert latitude/longitude to Minecraft coordinates
x, z = from_geo(48.856667, 2.350987)  # Paris coordinates
print(f"Minecraft coordinates: x={x}, z={z}")

# Convert Minecraft coordinates back to latitude/longitude
lat, lon = to_geo(x, z)
print(f"Geographic coordinates: lat={lat}, lon={lon}")
```

## API

### Functions

- `from_geo(lat: float, lon: float) -> Tuple[float, float]`: Convert geographic coordinates to Minecraft coordinates
- `to_geo(x: float, z: float) -> Tuple[float, float]`: Convert Minecraft coordinates to geographic coordinates
- `from_geo_object(lat: float, lon: float) -> Dict[str, float]`: Convert geographic coordinates to Minecraft coordinates (returns dict)  
- `to_geo_object(x: float, z: float) -> Dict[str, float]`: Convert Minecraft coordinates to geographic coordinates (returns dict)

## License

MIT License
