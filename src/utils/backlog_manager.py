"""
Project Backlog Management System

Provides consistent methodology for creating, updating, and managing 
project backlog items with persistence.

Version: 1.0.0
Author: Cloud Stack Generator Team
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class BacklogItem:
    """Represents a single backlog item"""
    
    id: str
    title: str
    description: str
    type: str  # feature, bug, task, technical_debt, research
    priority: str  # critical, high, medium, low
    status: str  # todo, in_progress, blocked, done
    labels: List[str] = field(default_factory=list)
    story_points: Optional[int] = None
    acceptance_criteria: List[str] = field(default_factory=list)
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    assigned_to: str = ""
    epic: str = ""
    dependencies: List[str] = field(default_factory=list)
    notes: str = ""


class BacklogManager:
    """Manages project backlog with persistent storage"""
    
    def __init__(self, backlog_file: str = None):
        if backlog_file is None:
            # Default to docs/project-backlog.yaml in project root
            project_root = Path(__file__).parent.parent.parent
            self.backlog_file = project_root / "docs" / "project-backlog.yaml"
        else:
            self.backlog_file = Path(backlog_file)
        
        self.backlog_data = self._load_backlog()
    
    def _load_backlog(self) -> Dict[str, Any]:
        """Load backlog from YAML file"""
        default_data = {
            "metadata": {
                "created": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "version": "1.0",
                "next_id": 1
            },
            "items": []
        }
        
        if not self.backlog_file.exists():
            return default_data
        
        try:
            with open(self.backlog_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data or "metadata" not in data:
                    return default_data
                
                # Ensure metadata has required fields
                if "next_id" not in data["metadata"]:
                    data["metadata"]["next_id"] = 1
                if "items" not in data:
                    data["items"] = []
                    
                return data
        except Exception as e:
            print(f"Error loading backlog: {e}")
            return default_data
    
    def _save_backlog(self) -> bool:
        """Save backlog to YAML file"""
        try:
            # Update metadata
            self.backlog_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            
            # Ensure directory exists
            self.backlog_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.backlog_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.backlog_data, f, default_flow_style=False, sort_keys=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving backlog: {e}")
            return False
    
    def _generate_id(self) -> str:
        """Generate unique backlog item ID"""
        next_id = self.backlog_data["metadata"].get("next_id", 1)
        item_id = f"BACK-{next_id:03d}"
        self.backlog_data["metadata"]["next_id"] = next_id + 1
        return item_id
    
    def add_item(self, 
                 title: str,
                 description: str,
                 item_type: str = "feature",
                 priority: str = "medium",
                 labels: List[str] = None,
                 story_points: int = None,
                 acceptance_criteria: List[str] = None,
                 epic: str = "",
                 assigned_to: str = "") -> str:
        """
        Add a new backlog item using consistent methodology
        
        Args:
            title: Brief descriptive title
            description: Detailed description of the work
            item_type: Type of work (feature, bug, task, technical_debt, research)
            priority: Priority level (critical, high, medium, low)
            labels: List of tags for categorization
            story_points: Effort estimation
            acceptance_criteria: List of completion criteria
            epic: Parent epic/theme
            assigned_to: Person responsible
            
        Returns:
            Generated item ID
        """
        item_id = self._generate_id()
        
        item = BacklogItem(
            id=item_id,
            title=title,
            description=description,
            type=item_type,
            priority=priority,
            status="todo",
            labels=labels or [],
            story_points=story_points,
            acceptance_criteria=acceptance_criteria or [],
            assigned_to=assigned_to,
            epic=epic
        )
        
        # Convert to dict for YAML serialization
        item_dict = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "type": item.type,
            "priority": item.priority,
            "status": item.status,
            "labels": item.labels,
            "story_points": item.story_points,
            "acceptance_criteria": item.acceptance_criteria,
            "created_date": item.created_date,
            "assigned_to": item.assigned_to,
            "epic": item.epic,
            "dependencies": item.dependencies,
            "notes": item.notes
        }
        
        self.backlog_data["items"].append(item_dict)
        
        if self._save_backlog():
            print(f"[SUCCESS] Backlog item {item_id} created: {title}")
            return item_id
        else:
            print(f"[ERROR] Failed to save backlog item {item_id}")
            return ""
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get backlog item by ID"""
        for item in self.backlog_data["items"]:
            if item["id"] == item_id:
                return item
        return None
    
    def update_item_status(self, item_id: str, status: str) -> bool:
        """Update status of backlog item"""
        for item in self.backlog_data["items"]:
            if item["id"] == item_id:
                item["status"] = status
                return self._save_backlog()
        return False
    
    def list_items(self, 
                   status: str = None, 
                   priority: str = None, 
                   item_type: str = None) -> List[Dict[str, Any]]:
        """List backlog items with optional filtering"""
        items = self.backlog_data["items"]
        
        if status:
            items = [item for item in items if item["status"] == status]
        if priority:
            items = [item for item in items if item["priority"] == priority]
        if item_type:
            items = [item for item in items if item["type"] == item_type]
            
        return items
    
    def print_summary(self):
        """Print backlog summary"""
        items = self.backlog_data["items"]
        total = len(items)
        
        if total == 0:
            print("[INFO] Backlog is empty")
            return
        
        # Count by status
        status_counts = {}
        priority_counts = {}
        type_counts = {}
        
        for item in items:
            status = item["status"]
            priority = item["priority"] 
            item_type = item["type"]
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        print(f"[SUMMARY] Backlog Summary ({total} items)")
        print(f"   Status: {dict(status_counts)}")
        print(f"   Priority: {dict(priority_counts)}")
        print(f"   Type: {dict(type_counts)}")


# Convenience function for adding items consistently
def add_backlog_item(title: str, 
                    description: str,
                    item_type: str = "feature",
                    priority: str = "medium",
                    labels: List[str] = None,
                    story_points: int = None,
                    acceptance_criteria: List[str] = None,
                    epic: str = "",
                    assigned_to: str = "") -> str:
    """
    Convenience function to add backlog item with consistent methodology
    
    This is the standard function to use when adding items to ensure 
    consistency across all backlog operations.
    """
    manager = BacklogManager()
    return manager.add_item(
        title=title,
        description=description,
        item_type=item_type,
        priority=priority,
        labels=labels,
        story_points=story_points,
        acceptance_criteria=acceptance_criteria,
        epic=epic,
        assigned_to=assigned_to
    )


if __name__ == "__main__":
    # Test the system
    manager = BacklogManager()
    manager.print_summary()