# Makefile for Attendance Assistant

.PHONY: help install install-dev test lint format clean build run docs

# 默认目标
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  build-exe    - Build executable"
	@echo "  run          - Run application"
	@echo "  docs         - Generate documentation"

# 安装依赖
install:
	uv sync --no-dev

install-dev:
	uv sync
	uv run pre-commit install

# 测试
test:
	uv run pytest

test-cov:
	uv run pytest --cov=attendance_assistant --cov-report=html

# 代码检查和格式化
lint:
	uv run flake8 attendance_assistant/ tests/
	uv run mypy attendance_assistant/

format:
	uv run black attendance_assistant/ tests/
	uv run isort attendance_assistant/ tests/

# 清理
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 构建
build:
	uv run python -m build

build-exe:
	uv run python scripts/build.py --exe

# 运行
run:
	uv run python -m attendance_assistant

# 文档
docs:
	@echo "Documentation generation not implemented yet"

# 开发环境设置
setup-dev:
	python scripts/setup_dev.py

# 完整的 CI 流程
ci: lint test

# 发布准备
release: clean lint test build