# TerrapyConvert Tests

## Overview

Simple test suite for validating coordinate conversion functionality.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization  
└── test_conversion.py       # Coordinate conversion tests
```

## Running Tests

```bash
pytest tests/
```

## Test Coverage

The test suite validates the exact coordinates specified in the requirements:

| Input | Expected Output | Status |
|-------|----------------|---------|
| (10, 20) | (3412228.818834, -380303.878966) | ✅ Perfect |
| (-5, 80) | (11585739.177302, 52072.379409) | ✅ Perfect |
| (65.5345, 5.534643) | (-7168241.215215, -11741455.592429) | ✅ Perfect |
