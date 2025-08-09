"""
Project setup script for SEO Authority Website Generator
Run this to set up your development environment
"""
import os
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
        "output"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if directory.startswith("src") or directory == "tests":
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Directory structure created")


def create_sample_files():
    """Create sample configuration and template files"""
    
    # Sample client config
    sample_config = """
client:
  business_name: "Sample Business"
  domain: "https://samplebusiness.com"
  industry: "Professional Services"
  
  contact:
    name: "Sample Business"
    address: "123 Main St, Anytown, ST 12345"
    phone: "+1-555-123-4567"
    
  social_media:
    facebook: "https://facebook.com/samplebusiness"
    linkedin: "https://linkedin.com/company/samplebusiness"
    
  branding:
    primary_color: "#007bff"
    secondary_color: "#6c757d"
    logo_url: "https://samplebusiness.com/logo.png"
    font_family: "Arial, sans-serif"
    
  pages:
    - title: "Home"
      slug: "index"
      primary_keyword: "professional services"
      secondary_keywords: ["local business", "expert solutions"]
      hero_image: "https://via.placeholder.com/1200x600"
      
  offerings:
    - name: "Consulting Services"
      description: "Expert consulting for your business needs"
      category: "Professional Service"
"""
    
    config_file = Path("config/sample_client_config.yaml")
    with open(config_file, 'w') as f:
        f.write(sample_config.strip())
    
    print("✅ Sample configuration files created")


def install_dependencies():
    """Install Python dependencies"""
    try:
        print("Installing dependencies...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements-dev.txt'
        ])
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("Please run: pip install -r requirements-dev.txt")


def setup_git_hooks():
    """Set up pre-commit hooks"""
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pre_commit', 'install'
        ])
        print("✅ Git hooks installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Pre-commit hooks not installed (optional)")


def run_initial_tests():
    """Run the initial test suite"""
    print("\nRunning initial tests...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests/', '-v'
        ], capture_output=True, text=True)
        
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
    print("Setting up SEO Authority Website Generator development environment...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Create project structure
    create_directory_structure()
    
    # Create sample files
    create_sample_files()
    
    # Install dependencies if requirements file exists
    if Path("requirements-dev.txt").exists():
        install_dependencies()
    else:
        print("⚠️  requirements-dev.txt not found, skipping dependency installation")
    
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