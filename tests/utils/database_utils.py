"""
This module contains utility functions for database operations.
"""

import alembic.config
from alembic import command


def migrate_to_db(
    script_location: str = "migrations",
    alembic_ini_path: str = "alembic.ini",
    connection=None,
    revision="head",
) -> None:
    """
    Migrates the database to a specific revision using Alembic.

    Args:
        script_location (str, optional): The location of the migration scripts.
            Defaults to "migrations".
        alembic_ini_path (str, optional): The path to the Alembic configuration file.
            Defaults to "alembic.ini".
        connection (Any, optional): The database connection. Defaults to None.
        revision (str, optional): The revision to migrate to. Defaults to "head".
    """
    config = alembic.config.Config(alembic_ini_path)
    if connection is not None:
        config.config_ini_section = "testdb"
        command.upgrade(config, revision)
