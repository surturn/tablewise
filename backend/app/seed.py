"""Compatibility entrypoint for seeding GrandPlatform demo data.

Run from repository root with:
    PYTHONPATH=backend python scripts/seed_grandplatform.py
"""
from backend.app.seed_grandplatform import main

__all__ = ["main"]
