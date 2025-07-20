"""
Test coordinate conversion functionality.
"""
import pytest
from terrapyconvert import from_geo, to_geo, from_geo_object, to_geo_object


def test_required_coordinates():
    """Test the specific coordinates from requirements."""
    test_cases = [
        (10, 20, 3412228.818833647, -380303.8789656482),
        (-5, 80, 11585739.177302402, 52072.37940910779),
        (65.5345, 5.534643, -7168241.215214804, -11741455.592429047),
    ]
    
    for lat, lon, expected_x, expected_z in test_cases:
        x, z = from_geo(lat, lon)
        assert x == pytest.approx(expected_x, abs=1e-6)
        assert z == pytest.approx(expected_z, abs=1e-6)


def test_object_api():
    """Test object-based API methods."""
    lat, lon = 10, 20
    
    # Test from_geo_object
    result = from_geo_object(lat, lon)
    assert isinstance(result, dict)
    assert "x" in result and "z" in result
    
    # Test to_geo_object
    geo_result = to_geo_object(result["x"], result["z"])
    assert isinstance(geo_result, dict)
    assert "lat" in geo_result and "lon" in geo_result


def test_api_consistency():
    """Test that tuple and object APIs return the same results."""
    lat, lon = 10, 20
    
    x_tuple, z_tuple = from_geo(lat, lon)
    result_obj = from_geo_object(lat, lon)
    
    assert x_tuple == result_obj["x"]
    assert z_tuple == result_obj["z"]


def test_to_geo_conversion():
    """Test the to_geo function using the sample test cases."""
    test_cases = [
        (10, 20, 3412228.818833647, -380303.8789656482),
        (-5, 80, 11585739.177302402, 52072.37940910779),
        (65.5345, 5.534643, -7168241.215214804, -11741455.592429047),
    ]
    
    for expected_lat, expected_lon, x, z in test_cases:
        lat, lon = to_geo(x, z)
        assert lat == pytest.approx(expected_lat, abs=1e-6)
        assert lon == pytest.approx(expected_lon, abs=1e-6)


def test_round_trip_conversion():
    """Test that from_geo and to_geo are inverse operations."""
    test_coordinates = [
        (0, 0),      # Equator, Prime Meridian
        (45, 90),    # 45N, 90E
        (-45, -90),  # 45S, 90W
        (10, 20),    # From test cases
        (-5, 80),    # From test cases
        (65.5345, 5.534643),  # From test cases
        (60, 0),     # High latitude, Prime Meridian
        (-60, 180),  # High latitude, Date Line
    ]
    
    for original_lat, original_lon in test_coordinates:
        # Forward conversion
        x, z = from_geo(original_lat, original_lon)
        
        # Backward conversion
        recovered_lat, recovered_lon = to_geo(x, z)
        
        # Check round-trip accuracy
        assert recovered_lat == pytest.approx(original_lat, abs=1e-6)
        assert recovered_lon == pytest.approx(original_lon, abs=1e-6)
