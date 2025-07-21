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
                    except Exception as decode_error:
                        raise ValueError(f"Could not decode base64 conformal data: {decode_error}")
                        
        except Exception as e:
            raise IOError(f"Failed to load conformal data from {conformal_file}: {e}")
    else:
        raise FileNotFoundError(f"Required conformal correction file not found: {conformal_file}")


def get_conformal_json() -> List[List[float]]:
    """Get conformal correction data as JSON."""
    return load_conformal_data()
