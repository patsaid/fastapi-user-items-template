"""
This file contains utility functions that can be used across the application.
"""

import uuid


def get_uuid():
    """
    Generate a random UUID.

    Returns:
        UUID: A randomly generated UUID.

    """

    return uuid.uuid4()
