from django.db import connection

USE_SQLITE_FTS = None  # True if sqlite FTS is available, False if not, None if untested


def SearchBackend(params):
    """
    Returns the appropriate search backend for the current 'default' database system
    """
    if connection.vendor == "postgresql":
        from .postgres.postgres import PostgresSearchBackend

        return PostgresSearchBackend(params)

    elif connection.vendor == "sqlite":
        global USE_SQLITE_FTS

        if USE_SQLITE_FTS is None:
            from .sqlite.utils import fts5_available, fts_table_exists

            if not fts5_available():
                USE_SQLITE_FTS = False
            elif not fts_table_exists():
                USE_SQLITE_FTS = False
            else:
                USE_SQLITE_FTS = True

        if USE_SQLITE_FTS:
            from .sqlite.sqlite import SQLiteSearchBackend

            return SQLiteSearchBackend(params)
        else:
            from .fallback import DatabaseSearchBackend

            return DatabaseSearchBackend(params)
    else:
        from .fallback import DatabaseSearchBackend

        return DatabaseSearchBackend(params)
