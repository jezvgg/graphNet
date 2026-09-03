"""Paths to application resources in a checkout, wheel or frozen bundle."""
from pathlib import Path


def resource_path(filename: str) -> Path:
    """Return a resource path independently of the working directory."""
    package_assets = Path(__file__).resolve().parent / "Assets"
    if package_assets.is_dir():
        return package_assets / filename
    return Path(__file__).resolve().parent.parent / "Assets" / filename
