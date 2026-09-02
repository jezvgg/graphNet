# Build with the locked Python environment, including the build dependency group.
.PHONY: all build
all: build

build:
	uv run --frozen --group build python scripts/build_exe.py
