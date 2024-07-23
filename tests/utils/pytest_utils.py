import pytest


def pytest_collection_modifyitems(items):
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
