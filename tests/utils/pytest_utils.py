"""
This module contains utility functions for pytest.

The pytest_utils module provides a function to modify the collection of test items
before running the tests. It adds markers to the test items based on their names.
"""

import pytest


def pytest_collection_modifyitems(items):
    """
    Modifies the collection of test items before running the tests.

    This function is called by pytest to modify the collection of test items
    before running the tests. It adds markers to the test items based on their names.

    Args:
        items (list): The list of test items.

    Returns:
        None
    """
    for item in items:
        if "model" in item.name:
            item.add_marker(pytest.mark.model)
        if "model_structure" in item.name:
            item.add_marker(pytest.mark.model_structure)
        if "unit" in item.name:
            item.add_marker(pytest.mark.unit)
        if "unit_schema" in item.name:
            item.add_marker(pytest.mark.unit_schema)
        if "integrate" in item.name:
            item.add_marker(pytest.mark.integrate)

        if "allo" in item.name:
            item.add_marker(pytest.mark.allo)
