"""
The main build module that transforms loaded data into a SQLite file.

This module takes the load results from the mhdata.load function,
and can use it to create a build result
"""

from .sql import build_sql_database
