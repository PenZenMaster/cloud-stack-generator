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


def create_test_files():
    """Create the initial test files"""

    # Create conftest.py
    conftest_content = '''"""
PyTest configuration and fixtures for the cloud stack generator tests
"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def sample_config_dict():
    """Complete sample configuration matching our specification"""
    return {
        "client": {
            "business_name": "Acme Professional Services",
            "domain": "https://acmeprofessional.com",
            "industry": "Professional Services",
            
            "contact": {
                "name": "Acme Professional Services",
                "address": "123 Main St, Anytown, ST 12345",
                "phone": "+1-555-123-4567"
            },
            
            "social_media": {
                "facebook": "https://facebook.com/acmepro",
                "twitter": "https://twitter.com/acmepro",
                "linkedin": "https://linkedin.com/company/acmepro",
                "instagram": "https://instagram.com/acmepro"
            },
            
            "google_maps": {
                "place_id": "ChIJExample123",
                "embed_url": "https://maps.google.com/embed?pb=example"
            },
            
            "branding": {
                "primary_color": "#FF5722",
                "secondary_color": "#FFC107",
                "logo_url": "https://acmeprofessional.com/logo.png",
                "font_family": "Roboto"
            },
            
            "pages": [
                {
                    "title": "Home",
                    "slug": "index",
                    "primary_keyword": "professional services",
                    "secondary_keywords": ["local business", "expert solutions"],
                    "hero_image": "https://images.unsplash.com/professional"
                },
                {
                    "title": "About Us", 
                    "slug": "about",
                    "primary_keyword": "experienced professionals",
                    "secondary_keywords": ["trusted advisors", "local experts"],
                    "hero_image": "https://images.unsplash.com/team"
                }
            ],
            
            "offerings": [
                {
                    "name": "Business Consulting",
                    "description": "Expert business consulting services",
                    "price_range": "$150-$300",
                    "category": "Professional Service"
                },
                {
                    "name": "Strategic Planning",
                    "description": "Comprehensive strategic planning services", 
                    "price_range": "$500-$1500",
                    "category": "Consulting"
                }
            ]
        }
    }


@pytest.fixture
def minimal_config_dict():
    """Minimal configuration with only required fields"""
    return {
        "client": {
            "business_name": "Test Business",
            "contact": {
                "phone": "+1-555-987-6543"
            },
            "pages": [
                {
                    "title": "Home",
                    "slug": "index"
                }
            ]
        }
    }


@pytest.fixture
def legacy_config_dict():
    """Configuration in your existing flat format for conversion testing"""
    return {
        "* Client Name": "Legacy Business Name",
        "* Business Category": "Professional Services",
        "* Phone": "(555) 123-4567",
        "Email": "info@legacy.com",
        "* Website": "https://legacy.com",
        "Street Address": "123 Main St",
        "City": "City",
        "State": "ST",
        "ZIP": "12345",
        "Country": "USA",
        "* Target Cities (one per line)": "Detroit\\nGrand Rapids\\nAnn Arbor",
        "* Services (one per line)": "Business Consulting\\nStrategic Planning\\nManagement Advice",
        "Social/Citation URLs (one per line)": 
            "https://facebook.com/legacy\\nhttps://linkedin.com/company/legacy",
        "Hero Image URL": "https://example.com/hero.jpg",
        "Logo URL": "https://example.com/logo.png",
        "Contact Email Address": "contact@legacy.com",
        "Primary Business Category": "Professional Services",
        "FAQ Questions (one per line)": 
            "What services do you offer?\\nHow much do you charge?"
    }


@pytest.fixture
def legacy_config_with_city_embeds():
    """Legacy config with city embed data"""
    return {
        "* Client Name": "Legacy Business Name",
        "* Phone": "(555) 123-4567",
        "* Target Cities (one per line)": "Detroit\\nGrand Rapids",
        "city_embeds": {
            "Detroit, MI": {
                "embed_code": "<iframe src='https://maps.google.com/embed?detroit'></iframe>"
            },
            "Grand Rapids, MI": {
                "embed_code": "<iframe src='https://maps.google.com/embed?grandrapids'></iframe>"
            }
        }
    }
'''

    # Create a simple initial test
    test_config_content = '''"""
Test suite for config_parser.py
Following TDD approach - these tests define the expected behavior
"""
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.core.config_parser import ConfigParser, ConfigValidationError
except ImportError:
    # Skip tests if modules not implemented yet
    pytest.skip("Config parser not implemented yet", allow_module_level=True)


class TestConfigParser:
    """Test suite for YAML configuration parsing and validation"""
    
    def test_config_parser_exists(self):
        """Test that ConfigParser class exists"""
        parser = ConfigParser()
        assert parser is not None
    
    def test_parse_valid_complete_config(self, sample_config_dict):
        """Test parsing a complete, valid configuration"""
        parser = ConfigParser()
        config = parser.parse(sample_config_dict)
        
        # Test client basic info
        assert config.client.business_name == "Acme Professional Services"
        assert config.client.domain == "https://acmeprofessional.com"
        assert config.client.industry == "Professional Services"
        
        # Test contact info (NAP)
        assert config.client.contact.name == "Acme Professional Services"
        assert config.client.contact.address == "123 Main St, Anytown, ST 12345"
        assert config.client.contact.phone == "+1-555-123-4567"
    
    def test_parse_minimal_required_config(self, minimal_config_dict):
        """Test parsing with only required fields"""
        parser = ConfigParser()
        config = parser.parse(minimal_config_dict)
        
        assert config.client.business_name == "Test Business"
        assert config.client.contact.phone == "+1-555-987-6543"
        assert len(config.client.pages) == 1
'''

    # Write the files
    with open("tests/conftest.py", "w") as f:
        f.write(conftest_content)

    with open("tests/test_config_parser.py", "w") as f:
        f.write(test_config_content)

    print("✅ Test files created")


def create_core_modules():
    """Create basic core module files"""

    # Create basic config_parser.py
    config_parser_content = '''"""
Configuration parser for the SEO Authority Website Generator
This implementation is driven by the test requirements
"""
import yaml
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass


@dataclass
class ContactInfo:
    """Contact information (NAP - Name, Address, Phone)"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: str = ""


@dataclass
class SocialMedia:
    """Social media account URLs"""
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None


@dataclass
class GoogleMaps:
    """Google Maps configuration"""
    place_id: Optional[str] = None
    embed_url: Optional[str] = None


@dataclass
class Branding:
    """Branding configuration"""
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    font_family: Optional[str] = None


@dataclass
class Page:
    """Page configuration"""
    title: str
    slug: str
    primary_keyword: Optional[str] = None
    secondary_keywords: List[str] = None
    hero_image: Optional[str] = None
    meta_description: Optional[str] = None
    
    def __post_init__(self):
        if self.secondary_keywords is None:
            self.secondary_keywords = []


@dataclass
class Offering:
    """Product or service offering"""
    name: str
    description: Optional[str] = None
    price_range: Optional[str] = None
    category: Optional[str] = None


@dataclass
class ClientConfig:
    """Complete client configuration"""
    business_name: str
    contact: ContactInfo
    pages: List[Page]
    offerings: List[Offering] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    social_media: Optional[SocialMedia] = None
    google_maps: Optional[GoogleMaps] = None
    branding: Optional[Branding] = None
    
    def __post_init__(self):
        if self.offerings is None:
            self.offerings = []


@dataclass
class Config:
    """Root configuration object"""
    client: ClientConfig


class ConfigParser:
    """Parser for YAML configuration files"""
    
    def parse(self, config_dict: Dict[str, Any]) -> Config:
        """Parse configuration dictionary into Config object"""
        client_data = config_dict.get("client", {})
        
        # Parse contact info
        contact_data = client_data.get("contact", {})
        contact = ContactInfo(
            name=contact_data.get("name"),
            address=contact_data.get("address"),
            phone=contact_data.get("phone", "")
        )
        
        # Parse social media
        social_data = client_data.get("social_media", {})
        social_media = SocialMedia(**social_data) if social_data else None
        
        # Parse Google Maps
        maps_data = client_data.get("google_maps", {})
        google_maps = GoogleMaps(**maps_data) if maps_data else None
        
        # Parse branding
        branding_data = client_data.get("branding", {})
        branding = Branding(**branding_data) if branding_data else None
        
        # Parse pages
        pages_data = client_data.get("pages", [])
        pages = [Page(**page_data) for page_data in pages_data]
        
        # Parse offerings
        offerings_data = client_data.get("offerings", [])
        offerings = [Offering(**offering_data) for offering_data in offerings_data]
        
        # Create client config
        client = ClientConfig(
            business_name=client_data.get("business_name", ""),
            domain=client_data.get("domain"),
            industry=client_data.get("industry"),
            contact=contact,
            social_media=social_media,
            google_maps=google_maps,
            branding=branding,
            pages=pages,
            offerings=offerings
        )
        
        return Config(client=client)
'''

    with open("src/core/config_parser.py", "w") as f:
        f.write(config_parser_content)

    print("✅ Core module files created")


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
    with open(config_file, "w") as f:
        f.write(sample_config.strip())

    print("✅ Sample configuration files created")


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
    print("Setting up SEO Authority Website Generator development environment...")
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

    # Create test files
    create_test_files()

    # Create core modules
    create_core_modules()

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
