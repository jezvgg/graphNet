"""Build the desktop application with the active Python environment."""
from pathlib import Path
import subprocess
import sys


def main():
    """Bundle dependencies and runtime assets beside the GraphNet executable."""
    root = Path(__file__).resolve().parents[1]
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
        "--onedir", "--windowed", "--name", "GraphNet",
        "--collect-all", "keras", "--collect-all", "tensorflow",
        "--collect-all", "librosa", "--collect-all", "dearpygui",
        "--copy-metadata", "keras", "--copy-metadata", "tensorflow",
        "--add-data", "Assets:Src/Assets", "main.py",
    ], cwd=root, check=True)


if __name__ == "__main__":
    main()
