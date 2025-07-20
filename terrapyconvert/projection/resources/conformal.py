"""
Conformal correction data loader.
"""
import json
import base64
from typing import List, Any
import os


def load_conformal_data() -> List[List[float]]:
    """
    Load conformal correction data.
    
    This function loads the conformal correction data from conformal.txt
    which contains the coordinate corrections for the BTE projection.
    
    Returns:
        2D array of conformal correction coordinates
    """
    # Try to load from conformal.txt
    conformal_file = os.path.join(os.path.dirname(__file__), 'conformal.txt')
    
    if os.path.exists(conformal_file):
        try:
            with open(conformal_file, 'r') as f:
                content = f.read().strip()
                
                # The file contains JSON array format
                if content.startswith('[[') or content.startswith('['):
                    print("Loading conformal correction data...")
                    data = json.loads(content)
                    print(f"Loaded {len(data)} conformal correction points")
                    return data
                else:
                    # Handle base64 encoded format if needed
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                        data = json.loads(decoded)
                        print(f"Loaded {len(data)} conformal correction points from base64")
                        return data
                    except:
                        print("Warning: Could not decode base64 conformal data")
                        
        except Exception as e:
            print(f"Warning: Could not load conformal data: {e}")
    else:
        print("Warning: conformal.txt not found, using dummy data")
    
    # Return dummy identity data if no conformal file available
    print("Using dummy conformal data - results will not be accurate")
    side_length = 256
    dummy_data = []
    
    counter = 0
    for v in range(side_length + 1):
        for u in range(side_length + 1 - v):
            # Create dummy coordinates that approximate the original pattern
            x_coord = (u / side_length - 0.5) * 0.8
            y_coord = (v / side_length - 0.3) * 0.8
            dummy_data.append([x_coord, y_coord])
            counter += 1
    
    return dummy_data


def get_conformal_json() -> List[List[float]]:
    """Get conformal correction data as JSON."""
    return load_conformal_data()
