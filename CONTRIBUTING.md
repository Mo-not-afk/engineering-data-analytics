# Contributing

Use Python 3.11 or newer. Create a virtual environment, install `-e ".[test]"`, and run `python -m unittest discover -s tests -v`. Keep generated databases, virtual environments and build output out of commits. Add tests for validation, persistence and API behavior when changing the corresponding layer. Clearly label synthetic data and avoid claiming it represents physical measurements.
