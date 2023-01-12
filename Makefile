all: qa

clean:
	rm -rf venv build dist .pytest_cache .mypy_cache *.egg-info

venv:
	python3.7 -m venv venv && \
		venv/bin/pip install --upgrade pip setuptools && \
		venv/bin/pip install --editable ".[dev]"

fmt: venv
	 venv/bin/isort . && venv/bin/black .

fmt-check: venv
	venv/bin/black --check . && venv/bin/isort --check .

lint: venv
	venv/bin/flake8

type-check: venv
	venv/bin/pyright

test: venv
	venv/bin/pytest --cov

sec-check:
	trivy filesystem --security-checks vuln .

qa: fmt-check lint type-check test sec-check

htmlcov: test
	venv/bin/coverage html

dist: clean qa
	venv/bin/pip wheel --wheel-dir dist --no-deps .
