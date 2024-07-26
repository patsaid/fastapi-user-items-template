"""
This module contains an enumeration representing the kind of token.
"""

from enum import Enum


class TokenKind(Enum):
    """Enumeration representing the kind of token."""

    REFESH_TOKEN = "refresh_token"
    ACCESS_TOKEN = "access_token"
