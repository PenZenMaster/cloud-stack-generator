"""
Module/Script Name: FAQ Manager
Path: src/core/content/faq_manager.py

Description:
Enhanced FAQ management system with bulk import/export, category management,
and search/filter capabilities.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-18

Last Modified Date:
2025-11-18

Comments:
* v1.00 - Initial FAQ manager with bulk operations and search
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from ..utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


class FAQCategory(Enum):
    """Standard FAQ categories"""
    GENERAL = "general"
    PRODUCTS = "products"
    SERVICES = "services"
    PRICING = "pricing"
    SHIPPING = "shipping"
    RETURNS = "returns"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    LOCATION = "location"
    OTHER = "other"


@dataclass
class EnhancedFAQItem:
    """Enhanced FAQ item with metadata and categorization"""

    question: str
    answer: str
    category: str = FAQCategory.GENERAL.value
    tags: List[str] = field(default_factory=list)
    priority: int = 0  # Higher = more important
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    active: bool = True

    # City-specific (optional)
    city_name: Optional[str] = None
    state: Optional[str] = None

    # SEO metadata (optional)
    schema_type: str = "Question"  # Schema.org type

    def __post_init__(self):
        """Validate FAQ item"""
        if not self.question:
            raise ValueError("FAQ question is required")
        if not self.answer:
            raise ValueError("FAQ answer is required")

        # Normalize category
        if isinstance(self.category, FAQCategory):
            self.category = self.category.value

        # Ensure tags is a list
        if isinstance(self.tags, str):
            self.tags = [tag.strip() for tag in self.tags.split(",")]

    def matches_search(self, search_term: str) -> bool:
        """Check if FAQ matches search term"""
        search_lower = search_term.lower()
        return (
            search_lower in self.question.lower() or
            search_lower in self.answer.lower() or
            any(search_lower in tag.lower() for tag in self.tags)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_legacy_format(self) -> Dict[str, str]:
        """Convert to legacy FAQItem format (question/answer only)"""
        return {
            "question": self.question,
            "answer": self.answer
        }


class FAQManager:
    """
    FAQ management system with import/export and search capabilities.

    Features:
    - Bulk import from CSV/JSON
    - Bulk export to CSV/JSON
    - Category management
    - Search and filter
    - Tag management
    """

    def __init__(self):
        """Initialize FAQ manager"""
        self.faqs: List[EnhancedFAQItem] = []
        logger.info("FAQ Manager initialized")

    def add_faq(self, faq: EnhancedFAQItem) -> None:
        """Add a single FAQ item"""
        self.faqs.append(faq)
        logger.info(
            f"Added FAQ: {faq.question[:50]}...",
            extra={"extra_fields": {"category": faq.category}}
        )

    def add_faqs(self, faqs: List[EnhancedFAQItem]) -> None:
        """Add multiple FAQ items"""
        self.faqs.extend(faqs)
        logger.info(f"Added {len(faqs)} FAQs")

    def remove_faq(self, question: str) -> bool:
        """Remove FAQ by question text"""
        initial_count = len(self.faqs)
        self.faqs = [faq for faq in self.faqs if faq.question != question]
        removed = initial_count - len(self.faqs)

        if removed > 0:
            logger.info(f"Removed {removed} FAQ(s) matching question")
            return True
        return False

    def get_faq_by_question(self, question: str) -> Optional[EnhancedFAQItem]:
        """Get FAQ by exact question match"""
        for faq in self.faqs:
            if faq.question == question:
                return faq
        return None

    def search(
        self,
        search_term: str = "",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        active_only: bool = True
    ) -> List[EnhancedFAQItem]:
        """
        Search and filter FAQs.

        Args:
            search_term: Search in question/answer/tags
            category: Filter by category
            tags: Filter by tags (any match)
            active_only: Only return active FAQs

        Returns:
            List of matching FAQ items
        """
        results = self.faqs

        # Filter by active status
        if active_only:
            results = [faq for faq in results if faq.active]

        # Filter by category
        if category:
            results = [faq for faq in results if faq.category == category]

        # Filter by tags
        if tags:
            results = [
                faq for faq in results
                if any(tag in faq.tags for tag in tags)
            ]

        # Filter by search term
        if search_term:
            results = [
                faq for faq in results
                if faq.matches_search(search_term)
            ]

        logger.debug(
            f"Search returned {len(results)} results",
            extra={"extra_fields": {
                "search_term": search_term,
                "category": category,
                "tags": tags
            }}
        )

        return results

    def get_by_category(self, category: str) -> List[EnhancedFAQItem]:
        """Get all FAQs in a specific category"""
        return self.search(category=category)

    def get_by_city(self, city_name: str) -> List[EnhancedFAQItem]:
        """Get all FAQs for a specific city"""
        return [
            faq for faq in self.faqs
            if faq.city_name and faq.city_name.lower() == city_name.lower()
        ]

    def get_categories(self) -> List[str]:
        """Get list of all categories in use"""
        return sorted(list(set(faq.category for faq in self.faqs)))

    def get_all_tags(self) -> Set[str]:
        """Get set of all tags in use"""
        all_tags = set()
        for faq in self.faqs:
            all_tags.update(faq.tags)
        return all_tags

    def get_statistics(self) -> Dict[str, Any]:
        """Get FAQ statistics"""
        active_faqs = [faq for faq in self.faqs if faq.active]

        category_counts = {}
        for faq in active_faqs:
            category_counts[faq.category] = category_counts.get(faq.category, 0) + 1

        city_counts = {}
        for faq in active_faqs:
            if faq.city_name:
                city_counts[faq.city_name] = city_counts.get(faq.city_name, 0) + 1

        return {
            "total_faqs": len(self.faqs),
            "active_faqs": len(active_faqs),
            "inactive_faqs": len(self.faqs) - len(active_faqs),
            "categories": category_counts,
            "cities": city_counts,
            "total_tags": len(self.get_all_tags())
        }

    # Import/Export Functions

    def import_from_csv(self, file_path: Path) -> int:
        """
        Import FAQs from CSV file.

        CSV Format:
        question,answer,category,tags,priority,active,city_name,state

        Returns:
            Number of FAQs imported
        """
        try:
            imported = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        # Parse tags
                        tags = []
                        if row.get('tags'):
                            tags = [tag.strip() for tag in row['tags'].split(',')]

                        # Parse active status
                        active = row.get('active', 'true').lower() in ('true', '1', 'yes')

                        # Parse priority
                        priority = int(row.get('priority', 0))

                        faq = EnhancedFAQItem(
                            question=row['question'],
                            answer=row['answer'],
                            category=row.get('category', FAQCategory.GENERAL.value),
                            tags=tags,
                            priority=priority,
                            active=active,
                            city_name=row.get('city_name') or None,
                            state=row.get('state') or None
                        )

                        self.add_faq(faq)
                        imported += 1

                    except Exception as e:
                        logger.warning(
                            "Skipping invalid CSV row",
                            extra={"extra_fields": {"error": str(e), "row": row}}
                        )
                        continue

            logger.info(f"Imported {imported} FAQs from CSV: {file_path}")
            return imported

        except Exception as e:
            logger.error(
                "Failed to import FAQs from CSV",
                extra={"extra_fields": {"file": str(file_path), "error": str(e)}}
            )
            raise

    def export_to_csv(self, file_path: Path, active_only: bool = False) -> int:
        """
        Export FAQs to CSV file.
        If no FAQs exist, exports a template CSV with headers only.

        Args:
            file_path: Output CSV file path
            active_only: Only export active FAQs

        Returns:
            Number of FAQs exported (0 if template exported)
        """
        try:
            faqs_to_export = self.faqs
            if active_only:
                faqs_to_export = [faq for faq in self.faqs if faq.active]

            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = [
                    'question', 'answer', 'category', 'tags', 'priority',
                    'active', 'city_name', 'state', 'created_date', 'modified_date'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                # If no FAQs to export, just write header (template)
                if len(faqs_to_export) == 0:
                    logger.info(f"Exported CSV template (no FAQs): {file_path}")
                    return 0

                for faq in faqs_to_export:
                    writer.writerow({
                        'question': faq.question,
                        'answer': faq.answer,
                        'category': faq.category,
                        'tags': ','.join(faq.tags),
                        'priority': faq.priority,
                        'active': faq.active,
                        'city_name': faq.city_name or '',
                        'state': faq.state or '',
                        'created_date': faq.created_date,
                        'modified_date': faq.modified_date
                    })

            logger.info(f"Exported {len(faqs_to_export)} FAQs to CSV: {file_path}")
            return len(faqs_to_export)

        except Exception as e:
            logger.error(
                "Failed to export FAQs to CSV",
                extra={"extra_fields": {"file": str(file_path), "error": str(e)}}
            )
            raise

    def import_from_json(self, file_path: Path) -> int:
        """
        Import FAQs from JSON file.

        JSON Format:
        [
            {
                "question": "...",
                "answer": "...",
                "category": "...",
                "tags": ["tag1", "tag2"],
                ...
            }
        ]

        Returns:
            Number of FAQs imported
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("JSON must be a list of FAQ objects")

            imported = 0
            for item in data:
                try:
                    faq = EnhancedFAQItem(**item)
                    self.add_faq(faq)
                    imported += 1
                except Exception as e:
                    logger.warning(
                        "Skipping invalid JSON item",
                        extra={"extra_fields": {"error": str(e), "item": item}}
                    )
                    continue

            logger.info(f"Imported {imported} FAQs from JSON: {file_path}")
            return imported

        except Exception as e:
            logger.error(
                "Failed to import FAQs from JSON",
                extra={"extra_fields": {"file": str(file_path), "error": str(e)}}
            )
            raise

    def export_to_json(
        self,
        file_path: Path,
        active_only: bool = False,
        pretty: bool = True
    ) -> int:
        """
        Export FAQs to JSON file.
        If no FAQs exist, exports a template JSON with one empty example.

        Args:
            file_path: Output JSON file path
            active_only: Only export active FAQs
            pretty: Pretty-print JSON

        Returns:
            Number of FAQs exported (0 if template exported)
        """
        try:
            faqs_to_export = self.faqs
            if active_only:
                faqs_to_export = [faq for faq in self.faqs if faq.active]

            # If no FAQs to export, create template with empty example
            if len(faqs_to_export) == 0:
                data = [{
                    "question": "",
                    "answer": "",
                    "category": "general",
                    "tags": [],
                    "priority": 0,
                    "active": True,
                    "city_name": None,
                    "state": None,
                    "created_date": "",
                    "modified_date": "",
                    "schema_type": "Question"
                }]
                logger.info(f"Exported JSON template (no FAQs): {file_path}")
            else:
                data = [faq.to_dict() for faq in faqs_to_export]

            with open(file_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)

            if len(faqs_to_export) > 0:
                logger.info(f"Exported {len(faqs_to_export)} FAQs to JSON: {file_path}")

            return len(faqs_to_export)

        except Exception as e:
            logger.error(
                "Failed to export FAQs to JSON",
                extra={"extra_fields": {"file": str(file_path), "error": str(e)}}
            )
            raise

    def export_to_legacy_format(self) -> List[Dict[str, str]]:
        """
        Export to legacy FAQ format (question/answer only).

        Useful for backward compatibility with existing config files.

        Returns:
            List of dicts with question/answer keys
        """
        return [faq.to_legacy_format() for faq in self.faqs if faq.active]

    def clear(self) -> None:
        """Clear all FAQs"""
        count = len(self.faqs)
        self.faqs.clear()
        logger.info(f"Cleared {count} FAQs")
