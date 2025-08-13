"""Project NorthStar contest package.

Convenience re-exports for public surface.

Copyright (c) 2025 Team NorthStar
Licensed under the MIT License. See LICENSE file for details.
"""

from .bigquery_client import BigQueryClient  # noqa: F401

__all__ = ["BigQueryClient"]
