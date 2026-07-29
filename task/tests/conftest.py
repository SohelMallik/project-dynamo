"""
pytest configuration for the argon-rdf-coordination verifier.

This file is automatically loaded by pytest before any test module.
It ensures the /app output directory exists so that file-existence
tests give clear "not found" errors rather than permission errors,
and configures pytest options used by the test suite.
"""

import os
import pytest


def pytest_configure(config):
    """Ensure /app exists before any test tries to open files there."""
    os.makedirs("/app", exist_ok=True)
