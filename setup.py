"""
Project setup script for SEO Authority Website Generator
Run this to set up your development environment

Version: 1.0.3
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import sys
import subprocess
from pathlib import Path


def create_directory_structure():
    """Create the project directory structure"""
    directories = [
        "src",
        "src/core",
        "src/templates",
        "src/templates/components",
        "src/templates/pages",
        "src/ui",
        "src/ui/dialogs",
        "src/utils",
        "tests",
        "tests/fixtures",
        "tests/fixtures/sample_configs",
        "config",
        "output",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

        # Create __init__.py files for Python packages
        if directory.startswith("src") or directory == "tests":
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()

    print("✅ Directory structure created")


def create_requirements_files():
    """Create requirements.txt and requirements-dev.txt"""

    requirements_txt = """PyQt6>=6.4.0
PyYAML>=6.0
Jinja2>=3.1.0
boto3>=1.26.0
requests>=2.28.0
Pillow>=9.3.0
beautifulsoup4>=4.11.0"""

    requirements_dev_txt = """-r requirements.txt
pytest>=7.2.0
pytest-qt>=4.2.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
black>=22.10.0
flake8>=5.0.0
mypy>=0.991
pre-commit>=2.20.0"""

    pytest_ini = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests  
    ui: UI tests requiring PyQt6
    aws: Tests requiring AWS credentials
    slow: Slow running tests

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning"""

    precommit_config = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML, types-requests]"""

    # Write requirements.txt
    with open("requirements.txt", "w") as f:
        f.write(requirements_txt)

    # Write requirements-dev.txt
    with open("requirements-dev.txt", "w") as f:
        f.write(requirements_dev_txt)

    # Write pytest.ini
    with open("pytest.ini", "w") as f:
        f.write(pytest_ini)

    # Write pre-commit config
    with open(".pre-commit-config.yaml", "w") as f:
        f.write(precommit_config)

    print("✅ Requirements and configuration files created")


def install_dependencies():
    """Install Python dependencies"""
    try:
        print("Installing dependencies...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"]
        )
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("Please run: pip install -r requirements-dev.txt")


def setup_git_hooks():
    """Set up pre-commit hooks"""
    try:
        subprocess.check_call([sys.executable, "-m", "pre_commit", "install"])
        print("✅ Git hooks installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Pre-commit hooks not installed (optional)")


def run_initial_tests():
    """Run the initial test suite"""
    print("\nRunning initial tests...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)

    except FileNotFoundError:
        print("⚠️  Tests not run - pytest not found")


def main():
    """Main setup function"""
    banner = "Setting up SEO Authority Website Generator development environment..."
    print(banner)
    print("=" * 60)

    # Check if we're in the right directory (setup.py should exist)
    if not Path("setup.py").exists():
        print("❌ Please run this script from the project root directory")
        print("The setup.py file should be in the current directory")
        sys.exit(1)

    # Create project structure
    create_directory_structure()

    # Create requirements files
    create_requirements_files()

    # Install dependencies if requirements file exists
    if Path("requirements-dev.txt").exists():
        install_dependencies()
    else:
        warning = "⚠️  requirements-dev.txt not found, skipping installation"
        print(warning)

    # Set up git hooks
    setup_git_hooks()

    # Run tests
    if Path("tests").exists():
        run_initial_tests()

    print("\n" + "=" * 60)
    print("🚀 Setup complete!")
    print("\nNext steps:")
    print("1. Copy your existing YAML builder files to src/ui/")
    print("2. Run: python main.py")
    print("3. Run tests: python -m pytest tests/ -v")
    print("4. Start implementing the failing tests!")
    print("\nHappy coding! 🎉")


if __name__ == "__main__":
    main()
