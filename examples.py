"""
Example usage of terrapyconvert package.
"""
import sys
import os

# Add the package to path for testing
sys.path.insert(0, os.path.dirname(__file__))

from terrapyconvert import from_geo, to_geo, from_geo_object, to_geo_object


def main():
    """Demonstrate basic usage of terrapyconvert."""
    
    print("TerrapyConvert Usage Examples")
    print("=" * 40)
    print()
    
    # Example 1: Convert famous locations
    locations = [
        ("Paris, France", 48.856667, 2.350987),
        ("New York, USA", 40.714268, -74.005974),
        ("Tokyo, Japan", 35.676667, 139.650000),
        ("Sydney, Australia", -33.865143, 151.209900),
        ("Cairo, Egypt", 30.033333, 31.233334),
    ]
    
    print("Converting famous world locations:")
    print("-" * 40)
    
    for name, lat, lon in locations:
        # Convert to Minecraft coordinates
        x, z = from_geo(lat, lon)
        
        # Convert back to verify
        lat_back, lon_back = to_geo(x, z)
        
        print(f"{name}:")
        print(f"  Real coordinates: {lat}°N, {lon}°E")
        print(f"  Minecraft coords: x={x:,.0f}, z={z:,.0f}")
        print(f"  Round trip: {lat_back:.6f}°N, {lon_back:.6f}°E")
        print()
    
    # Example 2: Using object methods
    print("\nUsing object-based methods:")
    print("-" * 40)
    
    test_lat, test_lon = 51.5074, -0.1278  # London
    
    # Get result as dictionary
    mc_coords = from_geo_object(test_lat, test_lon)
    geo_coords = to_geo_object(mc_coords['x'], mc_coords['z'])
    
    print(f"London coordinates:")
    print(f"  Input: {test_lat}°N, {test_lon}°E")
    print(f"  Minecraft: {mc_coords}")
    print(f"  Back to geo: {geo_coords}")
    
    # Example 3: Working with the test coordinates
    print("\nTest coordinates from requirements:")
    print("-" * 40)
    
    test_cases = [
        (10, 20),
        (-5, 80),
        (65.5345, 5.534643),
    ]
    
    for i, (lat, lon) in enumerate(test_cases, 1):
        x, z = from_geo(lat, lon)
        print(f"Test {i}: ({lat}, {lon}) -> ({x:,.6f}, {z:,.6f})")


if __name__ == "__main__":
    main()
