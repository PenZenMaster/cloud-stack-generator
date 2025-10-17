"""
GitHub Issues Creator
Automatically create GitHub issues from templates for the cloud-stack-generator project
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from github_token_manager import GitHubTokenManager


@dataclass
class GitHubIssue:
    """GitHub issue data structure"""

    title: str
    body: str
    labels: List[str]
    assignees: List[str] = None
    milestone: Optional[str] = None

    def to_api_dict(self) -> Dict:
        """Convert to GitHub API format"""
        data = {"title": self.title, "body": self.body, "labels": self.labels}
        if self.assignees:
            data["assignees"] = self.assignees
        return data


class GitHubIssuesCreator:
    """Create and manage GitHub issues via API"""

    def __init__(
        self, repo_owner: str = "PenZenMaster", repo_name: str = "cloud-stack-generator"
    ):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = "https://api.github.com"
        self.token_manager = GitHubTokenManager()
        self.token = self.token_manager.get_token()

        if not self.token:
            raise ValueError("GitHub token not found. Please run setup first.")

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "cloud-stack-generator-issue-creator",
        }

    def create_issue(self, issue: GitHubIssue) -> Optional[Dict]:
        """Create a single GitHub issue"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"

        try:
            response = requests.post(
                url, headers=self.headers, json=issue.to_api_dict()
            )

            if response.status_code == 201:
                issue_data = response.json()
                print(f"✅ Created issue #{issue_data['number']}: {issue.title}")
                return issue_data
            else:
                print(
                    f"❌ Failed to create issue '{issue.title}': {response.status_code}"
                )
                print(f"   Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error creating issue '{issue.title}': {e}")
            return None

    def create_template_import_export_issues(self) -> List[Dict]:
        """Create all Template Import/Export feature issues"""

        issues = [
            GitHubIssue(
                title="Core Template Import/Export Infrastructure",
                body=self._get_issue_1_body(),
                labels=["feature", "enhancement", "template-system", "high-priority"],
            ),
            GitHubIssue(
                title="Template Selection Dialog Enhancement - Add Import/Export Functionality",
                body=self._get_issue_2_body(),
                labels=["ui", "enhancement", "template-system", "high-priority"],
            ),
            GitHubIssue(
                title="Add Template Import/Export to Branding & Style Tab",
                body=self._get_issue_3_body(),
                labels=["ui", "enhancement", "branding", "medium-priority"],
            ),
            GitHubIssue(
                title="Implement Dynamic Template Discovery and Refresh",
                body=self._get_issue_4_body(),
                labels=["core", "template-system", "enhancement", "medium-priority"],
            ),
            GitHubIssue(
                title="Define and Document Template Package Format",
                body=self._get_issue_5_body(),
                labels=[
                    "documentation",
                    "specification",
                    "template-system",
                    "medium-priority",
                ],
            ),
            GitHubIssue(
                title="Create Comprehensive Test Suite for Template Import/Export",
                body=self._get_issue_6_body(),
                labels=[
                    "testing",
                    "quality-assurance",
                    "template-system",
                    "medium-priority",
                ],
            ),
            GitHubIssue(
                title="Prepare Infrastructure for Future Template Marketplace",
                body=self._get_issue_7_body(),
                labels=[
                    "future-enhancement",
                    "marketplace",
                    "template-system",
                    "low-priority",
                ],
            ),
        ]

        created_issues = []
        print(f"🚀 Creating {len(issues)} issues for Template Import/Export feature...")
        print("=" * 60)

        for issue in issues:
            result = self.create_issue(issue)
            if result:
                created_issues.append(result)

        print("=" * 60)
        print(
            f"✅ Successfully created {len(created_issues)} out of {len(issues)} issues"
        )

        return created_issues

    def create_project_board(self, name: str, description: str) -> Optional[Dict]:
        """Create a GitHub project board"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/projects"

        data = {"name": name, "body": description}

        try:
            response = requests.post(url, headers=self.headers, json=data)

            if response.status_code == 201:
                project_data = response.json()
                print(f"✅ Created project board: {name}")
                return project_data
            else:
                print(f"❌ Failed to create project board: {response.status_code}")
                print(f"   Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error creating project board: {e}")
            return None

    def get_repository_info(self) -> Optional[Dict]:
        """Get repository information to verify access"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                repo_data = response.json()
                print(f"✅ Repository access verified: {repo_data['full_name']}")
                print(
                    f"   Description: {repo_data.get('description', 'No description')}"
                )
                print(f"   Language: {repo_data.get('language', 'Unknown')}")
                print(f"   Stars: {repo_data.get('stargazers_count', 0)}")
                return repo_data
            else:
                print(f"❌ Failed to access repository: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error accessing repository: {e}")
            return None

    def list_existing_issues(self, state: str = "open") -> List[Dict]:
        """List existing issues in the repository"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"
        params = {"state": state}

        try:
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 200:
                issues = response.json()
                print(f"📋 Found {len(issues)} {state} issues")
                return issues
            else:
                print(f"❌ Failed to list issues: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error listing issues: {e}")
            return []

    def _get_issue_1_body(self) -> str:
        return """## 🎯 Objective
Implement the core infrastructure for template import/export functionality to enable users to export existing templates for external editing and import custom templates.

## 📋 Background
Users currently cannot export templates for external editing or import custom templates. The basic infrastructure exists but needs completion and enhancement.

## ✅ Acceptance Criteria
- [ ] Complete `TemplateExporter.export_template_package()` method with proper error handling
- [ ] Complete `TemplateImporter.import_template_package()` method with validation
- [ ] Implement template package validation system
- [ ] Add progress indicators for import/export operations
- [ ] Ensure exported packages include all necessary files (template.html, metadata.json, README.md)
- [ ] Handle template ID conflicts during import
- [ ] Add comprehensive error handling and user feedback

## 🔧 Technical Tasks
- [ ] Complete stubbed methods in `src/core/templates/template_export.py`
- [ ] Add file validation for template packages
- [ ] Implement metadata validation during import
- [ ] Add conflict resolution for duplicate template IDs
- [ ] Create template package structure documentation

## 📁 Files to Modify
- `src/core/templates/template_export.py`
- `src/core/templates/template_manager.py`

## 🏁 Definition of Done
- All acceptance criteria met
- Unit tests written and passing
- Integration tests verify end-to-end workflow
- Error handling covers all edge cases
- Code reviewed and merged

## ⏱️ Estimated Effort
3-4 days

## 🔗 Related Issues
- Depends on: Template Selection Dialog Enhancement
- Relates to: Dynamic Template Discovery System"""

    def _get_issue_2_body(self) -> str:
        return """## 🎯 Objective
Enhance the template selection dialog to include fully functional import and export capabilities with proper UI integration and user feedback.

## 📋 Background
The template selection dialog currently has placeholder import/export methods that need to be replaced with full functionality.

## ✅ Acceptance Criteria
- [ ] Replace placeholder import/export methods with full functionality
- [ ] Add file dialogs for template package selection/saving
- [ ] Implement progress dialogs for long-running operations
- [ ] Auto-refresh template list after successful import
- [ ] Auto-select newly imported templates
- [ ] Provide clear success/error messages to users
- [ ] Maintain consistent UI styling with existing dialog

## 🔧 Technical Tasks
- [ ] Replace stubbed methods in `src/ui/dialogs/template_selection_dialog.py`
- [ ] Add proper file dialog integration
- [ ] Implement progress tracking for import/export
- [ ] Add template list refresh functionality
- [ ] Update UI styling for new buttons

## 📁 Files to Modify
- `src/ui/dialogs/template_selection_dialog.py`

## 🏁 Definition of Done
- Import/export buttons fully functional
- User experience is smooth and intuitive
- Error cases handled gracefully
- UI remains responsive during operations

## ⏱️ Estimated Effort
2-3 days

## 🔗 Related Issues
- Depends on: Core Template Import/Export Infrastructure
- Relates to: Branding Tab Template Management"""

    def _get_issue_3_body(self) -> str:
        return """## 🎯 Objective
Add template management capabilities directly to the Branding & Style tab for easier access to import/export functionality.

## 📋 Background
Users should be able to access template import/export functionality directly from the Branding & Style tab for better workflow integration.

## ✅ Acceptance Criteria
- [ ] Add "Import Template" button to branding tab
- [ ] Add "Export Current" button to branding tab
- [ ] Implement proper button styling consistent with existing design
- [ ] Connect buttons to import/export functionality
- [ ] Update template display after successful import
- [ ] Show current template information clearly

## 🔧 Technical Tasks
- [ ] Add new buttons to `src/ui/components/branding_tab.py`
- [ ] Implement `_import_template()` method
- [ ] Implement `_export_current_template()` method
- [ ] Add proper error handling and user feedback
- [ ] Update template display refresh logic

## 📁 Files to Modify
- `src/ui/components/branding_tab.py`

## 🏁 Definition of Done
- Buttons appear in branding tab with proper styling
- Import/export functionality works from branding tab
- Template system refreshes properly after operations
- User feedback is clear and helpful

## ⏱️ Estimated Effort
2 days

## 🔗 Related Issues
- Depends on: Template Selection Dialog Enhancement
- Relates to: Dynamic Template Discovery System"""

    def _get_issue_4_body(self) -> str:
        return """## 🎯 Objective
Enhance the template manager to dynamically discover imported templates and refresh the template registry without requiring application restart.

## 📋 Background
Currently, imported templates may not appear immediately in the template selection without restarting the application.

## ✅ Acceptance Criteria
- [ ] Add `refresh_templates()` method to TemplateManager
- [ ] Ensure imported templates appear in selection dialog immediately
- [ ] Support templates in `imported/` subdirectory
- [ ] Maintain template registry consistency
- [ ] Update Jinja environment when new templates added
- [ ] Preserve existing template functionality

## 🔧 Technical Tasks
- [ ] Enhance `src/core/templates/template_manager.py`
- [ ] Add template directory monitoring
- [ ] Implement registry refresh functionality
- [ ] Update template discovery logic
- [ ] Test with various template locations

## 📁 Files to Modify
- `src/core/templates/template_manager.py`

## 🏁 Definition of Done
- Templates discovered dynamically
- Registry updates without restart
- All template operations work with imported templates
- No regression in existing functionality

## ⏱️ Estimated Effort
2 days

## 🔗 Related Issues
- Supports: All template import/export features
- Relates to: Core Template Import/Export Infrastructure"""

    def _get_issue_5_body(self) -> str:
        return """## 🎯 Objective
Create comprehensive documentation for the template package format to enable external template creation and ensure consistency.

## 📋 Background
External developers and designers need clear documentation to create compatible template packages.

## ✅ Acceptance Criteria
- [ ] Document template package structure (zip format)
- [ ] Define metadata.json schema with validation rules
- [ ] Create template creation guidelines for external developers
- [ ] Document required vs optional template variables
- [ ] Provide example template packages
- [ ] Create troubleshooting guide for common import issues

## 📝 Deliverables
- [ ] Template package format specification document
- [ ] Template creation guide for external developers
- [ ] Example template packages for testing
- [ ] Metadata schema documentation
- [ ] Import/export user guide

## 📁 Files to Create
- `docs/TEMPLATE_PACKAGE_FORMAT.md`
- `docs/TEMPLATE_CREATION_GUIDE.md`
- `examples/sample_template_package.zip`

## 🏁 Definition of Done
- Complete documentation available
- External developers can create compatible templates
- All package format details documented
- Examples provided and tested

## ⏱️ Estimated Effort
1-2 days

## 🔗 Related Issues
- Supports: All template import/export features
- Enables: Community template development"""

    def _get_issue_6_body(self) -> str:
        return """## 🎯 Objective
Develop comprehensive test suite to ensure template import/export functionality is robust and handles all edge cases properly.

## 📋 Background
Template import/export functionality needs thorough testing to ensure reliability and user confidence.

## ✅ Acceptance Criteria
- [ ] Unit tests for TemplateExporter and TemplateImporter classes
- [ ] Integration tests for end-to-end import/export workflow
- [ ] UI tests for template selection dialog functionality
- [ ] Error handling tests for malformed packages
- [ ] Performance tests for large template packages
- [ ] Regression tests for existing template functionality

## 🧪 Test Coverage Areas
- [ ] Template package creation and extraction
- [ ] Metadata validation and parsing
- [ ] Template file validation
- [ ] Import conflict detection and resolution
- [ ] UI integration and user feedback
- [ ] File system operations and permissions

## 📁 Files to Create
- `tests/test_template_export.py`
- `tests/test_template_import.py`
- `tests/test_template_ui.py`
- `tests/fixtures/sample_templates/`

## 🏁 Definition of Done
- Test coverage >90% for template import/export code
- All edge cases covered
- Tests pass consistently
- Continuous integration setup

## ⏱️ Estimated Effort
2-3 days

## 🔗 Related Issues
- Tests: All template import/export features
- Ensures: Quality and reliability"""

    def _get_issue_7_body(self) -> str:
        return """## 🎯 Objective
Lay groundwork for future template marketplace by implementing template collections, versioning, and sharing capabilities.

## 📋 Background
Future marketplace features will require additional infrastructure for template management and sharing.

## ✅ Acceptance Criteria
- [ ] Implement template collection import/export
- [ ] Add template versioning and update detection
- [ ] Create template sharing format with digital signatures
- [ ] Implement template dependency resolution
- [ ] Add template rating and review metadata
- [ ] Create template submission validation

## 🚀 Future Features (Out of Scope)
- [ ] Template marketplace integration
- [ ] Automatic template updates
- [ ] Template dependency management
- [ ] Community template sharing
- [ ] Template licensing support

## 📁 Files to Enhance
- `src/core/templates/template_export.py` (collection support)
- `src/core/templates/template_manager.py` (versioning)
- New: `src/core/templates/marketplace.py`

## 🏁 Definition of Done
- Foundation ready for marketplace features
- Collection import/export working
- Versioning system implemented
- Architecture supports future expansion

## ⏱️ Estimated Effort
3-4 days

## 🔗 Related Issues
- Builds on: All template import/export features
- Enables: Future marketplace development"""


def main():
    """Main function to create GitHub issues"""
    print("🚀 GitHub Issues Creator for Cloud Stack Generator")
    print("=" * 60)

    try:
        # Initialize the creator
        creator = GitHubIssuesCreator()

        # Verify repository access
        repo_info = creator.get_repository_info()
        if not repo_info:
            print(
                "❌ Failed to access repository. Please check your token permissions."
            )
            return

        print()

        # List existing issues
        existing_issues = creator.list_existing_issues()
        if existing_issues:
            print("\n📋 Existing issues:")
            for issue in existing_issues[:5]:  # Show first 5
                print(f"   #{issue['number']}: {issue['title']}")
            if len(existing_issues) > 5:
                print(f"   ... and {len(existing_issues) - 5} more")

        print()

        # Ask user confirmation
        response = (
            input("🤔 Do you want to create the Template Import/Export issues? (y/N): ")
            .strip()
            .lower()
        )
        if response not in ["y", "yes"]:
            print("❌ Operation cancelled.")
            return

        # Create the issues
        created_issues = creator.create_template_import_export_issues()

        if created_issues:
            print("\n🎉 Issues created successfully!")
            print("\n📋 Created issues:")
            for issue in created_issues:
                print(f"   #{issue['number']}: {issue['title']}")
                print(f"      URL: {issue['html_url']}")

            print(f"\n✅ Visit your repository to see the issues:")
            print(f"   https://github.com/PenZenMaster/cloud-stack-generator/issues")

        else:
            print("\n❌ No issues were created.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
