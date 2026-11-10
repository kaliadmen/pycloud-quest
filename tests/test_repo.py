"""Repo-level sanity checks. If these fail, the setup is broken, not your lesson code."""

import sys

import nimbus


def test_python_version_is_supported():
    assert sys.version_info >= (3, 12), "Run through `uv run` so the project's Python is used."


def test_nimbus_package_imports():
    assert nimbus.__version__
