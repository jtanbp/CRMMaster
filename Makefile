.PHONY: install dev test lint requirements clean

# Install only runtime dependencies
install:
	pip install .

# Install dev dependencies (flake8, pytest, pip-tools, etc.)
dev:
	pip install .[dev]

# Run tests with pytest
test:
	pytest

# Run flake8 linting
lint:
	flake8 src tests

# Export requirements.txt from pyproject.toml
requirements:
	pip-compile pyproject.toml --output-file=requirements.txt

# Clean build artifacts
clean:
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
