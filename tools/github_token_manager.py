"""
GitHub Token Management
Secure handling of GitHub Personal Access Token
"""

import os
from pathlib import Path
from typing import Optional


class GitHubTokenManager:
    """Manages GitHub token securely from multiple sources"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = Path(project_root)
        self.env_file = self.project_root / ".env"

    def get_token(self) -> Optional[str]:
        """
        Get GitHub token from secure sources in priority order:
        1. Environment variable GITHUB_TOKEN
        2. .env file in project root
        3. Windows Credential Manager (if available)

        Returns:
            str: GitHub token if found, None otherwise
        """

        # 1. Check environment variable first (highest priority)
        token = os.getenv("GITHUB_TOKEN")
        if token and token != "your_token_here":
            return token

        # 2. Check .env file
        token = self._load_from_env_file()
        if token and token != "your_token_here":
            return token

        # 3. Check Windows Credential Manager (if available)
        token = self._load_from_credential_manager()
        if token:
            return token

        return None

    def _load_from_env_file(self) -> Optional[str]:
        """Load token from .env file"""
        try:
            if self.env_file.exists():
                with open(self.env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GITHUB_TOKEN="):
                            token = line.split("=", 1)[1].strip()
                            if token and token != "your_token_here":
                                return token
        except Exception as e:
            print(f"Error reading .env file: {e}")
        return None

    def _load_from_credential_manager(self) -> Optional[str]:
        """Load token from Windows Credential Manager (Windows only)"""
        try:
            import keyring

            return keyring.get_password("github", "cloud-stack-generator")
        except ImportError:
            # keyring not available
            return None
        except Exception:
            # Other errors (not Windows, no credential, etc.)
            return None

    def store_in_credential_manager(self, token: str) -> bool:
        """
        Store token in Windows Credential Manager for secure storage

        Args:
            token: GitHub Personal Access Token

        Returns:
            bool: True if stored successfully, False otherwise
        """
        try:
            import keyring

            keyring.set_password("github", "cloud-stack-generator", token)
            print("✅ Token stored securely in Windows Credential Manager")
            return True
        except ImportError:
            print("❌ keyring package not available. Install with: pip install keyring")
            return False
        except Exception as e:
            print(f"❌ Error storing token: {e}")
            return False

    def validate_token(self, token: str) -> bool:
        """
        Validate that the token works with GitHub API

        Args:
            token: GitHub Personal Access Token

        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            import requests

            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            response = requests.get(
                "https://api.github.com/user", headers=headers, timeout=10
            )

            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Token valid for user: {user_info.get('login', 'Unknown')}")
                return True
            else:
                print(f"❌ Token validation failed: {response.status_code}")
                return False

        except ImportError:
            print(
                "❌ requests package not available. Install with: pip install requests"
            )
            return False
        except Exception as e:
            print(f"❌ Error validating token: {e}")
            return False

    def setup_token_interactive(self):
        """Interactive setup for GitHub token"""
        print("🔑 GitHub Token Setup")
        print("=" * 50)

        # Check if token already exists
        existing_token = self.get_token()
        if existing_token:
            print("✅ Token already configured")
            if self.validate_token(existing_token):
                print("✅ Token is valid and working")
                return existing_token
            else:
                print("❌ Existing token is invalid, please set up a new one")

        print("\n📋 How to get a GitHub Personal Access Token:")
        print("1. Go to GitHub.com → Settings → Developer settings")
        print("2. Click 'Personal access tokens' → 'Tokens (classic)'")
        print("3. Click 'Generate new token (classic)'")
        print("4. Select scopes: 'repo' and 'project'")
        print("5. Copy the generated token")

        token = input("\n🔐 Paste your GitHub token here: ").strip()

        if not token or token == "your_token_here":
            print("❌ No token provided")
            return None

        # Validate the token
        if not self.validate_token(token):
            print("❌ Invalid token provided")
            return None

        # Store the token
        print("\n💾 Choose storage method:")
        print("1. Environment file (.env) - Good for development")
        print("2. Windows Credential Manager - Most secure")
        print("3. Environment variable - For CI/CD")

        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            self._store_in_env_file(token)
        elif choice == "2":
            self.store_in_credential_manager(token)
        elif choice == "3":
            print("\n📝 Add this to your environment:")
            print(f"set GITHUB_TOKEN={token}")
            print("Or in PowerShell:")
            print(f"$env:GITHUB_TOKEN='{token}'")
        else:
            print("❌ Invalid choice, storing in .env file by default")
            self._store_in_env_file(token)

        return token

    def _store_in_env_file(self, token: str):
        """Store token in .env file"""
        try:
            # Read existing content
            lines = []
            if self.env_file.exists():
                with open(self.env_file, "r") as f:
                    lines = f.readlines()

            # Update or add GITHUB_TOKEN line
            token_line = f"GITHUB_TOKEN={token}\n"
            found = False

            for i, line in enumerate(lines):
                if line.startswith("GITHUB_TOKEN="):
                    lines[i] = token_line
                    found = True
                    break

            if not found:
                lines.append(token_line)

            # Write back to file
            with open(self.env_file, "w") as f:
                f.writelines(lines)

            print(f"✅ Token stored in {self.env_file}")
            print("⚠️  Make sure .env is in your .gitignore file!")

        except Exception as e:
            print(f"❌ Error storing token in .env file: {e}")


def main():
    """Interactive token setup"""
    manager = GitHubTokenManager()
    token = manager.setup_token_interactive()

    if token:
        print("\n🎉 GitHub token setup complete!")
        print("You can now use GitHub API integration.")
    else:
        print("\n❌ Token setup failed.")


if __name__ == "__main__":
    main()
