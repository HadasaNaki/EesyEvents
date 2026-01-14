# Makefile for EasyEvents

.PHONY: help install test lint format clean run docker-build docker-run

PYTHON := python
PIP := pip
PYTEST := pytest

help:
	@echo "EasyEvents Makefile"
	@echo "-------------------"
	@echo "make install      Install dependencies"
	@echo "make test         Run tests"
	@echo "make lint         Run linting (flake8)"
	@echo "make format       Run pre-commit hooks manually"
	@echo "make run          Run local server"
	@echo "make docker-build Build Docker image"
	@echo "make docker-run   Run with Docker Compose"
	@echo "make clean        Remove cache files"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-html pre-commit
	pre-commit install

test:
	$(PYTEST)

lint:
	flake8 .

format:
	pre-commit run --all-files

run:
	$(PYTHON) run_server.py

docker-build:
	docker-compose build

docker-run:
	docker-compose up

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage tests/report.html
