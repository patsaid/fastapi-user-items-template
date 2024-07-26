"""
This module contains utility functions for authentication.

Functions:
- hash_pass(password: str) -> str: Hashes the given password using bcrypt
    and returns the hashed password as a string.
- verify_password(non_hashed_pass: str, hashed_pass: str) -> bool: Verifies if the non-hashed
    password matches the hashed password using bcrypt and returns a boolean value indicating
    the result.
"""

import bcrypt


def hash_pass(password: str):
    """
    Hashes the given password using bcrypt.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.

    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)

    return hashed_password.decode("utf-8")


def verify_password(non_hashed_pass, hashed_pass):
    """
    Verify if a non-hashed password matches a hashed password.

    Args:
        non_hashed_pass (str): The non-hashed password to verify.
        hashed_pass (str): The hashed password to compare against.

    Returns:
        bool: True if the non-hashed password matches the hashed password, False otherwise.
    """
    password_byte_enc = non_hashed_pass.encode("utf-8")
    hashed_pass = hashed_pass.encode("utf-8")

    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_pass)
