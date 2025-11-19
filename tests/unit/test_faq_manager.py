"""
Unit tests for FAQ Manager
Tests bulk import/export, search, and category management
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import csv

from src.core.content.faq_manager import (
    FAQManager,
    EnhancedFAQItem,
    FAQCategory
)


@pytest.mark.unit
class TestEnhancedFAQItem:
    """Test EnhancedFAQItem model"""

    def test_basic_creation(self):
        """Test basic FAQ item creation"""
        faq = EnhancedFAQItem(
            question="Test question?",
            answer="Test answer"
        )

        assert faq.question == "Test question?"
        assert faq.answer == "Test answer"
        assert faq.category == FAQCategory.GENERAL.value
        assert faq.active is True
        assert isinstance(faq.tags, list)

    def test_with_category(self):
        """Test FAQ with specific category"""
        faq = EnhancedFAQItem(
            question="Q",
            answer="A",
            category=FAQCategory.PRODUCTS.value
        )

        assert faq.category == "products"

    def test_with_tags(self):
        """Test FAQ with tags"""
        faq = EnhancedFAQItem(
            question="Q",
            answer="A",
            tags=["tag1", "tag2", "tag3"]
        )

        assert len(faq.tags) == 3
        assert "tag1" in faq.tags

    def test_tags_from_string(self):
        """Test automatic tag parsing from comma-separated string"""
        faq = EnhancedFAQItem(
            question="Q",
            answer="A",
            tags="tag1, tag2, tag3"
        )

        assert len(faq.tags) == 3
        assert "tag1" in faq.tags

    def test_city_specific(self):
        """Test city-specific FAQ"""
        faq = EnhancedFAQItem(
            question="Do you serve Orlando?",
            answer="Yes",
            city_name="Orlando",
            state="FL"
        )

        assert faq.city_name == "Orlando"
        assert faq.state == "FL"

    def test_matches_search(self):
        """Test search matching"""
        faq = EnhancedFAQItem(
            question="What are your hours?",
            answer="We are open 9-5",
            tags=["hours", "schedule"]
        )

        assert faq.matches_search("hours")
        assert faq.matches_search("open")
        assert faq.matches_search("schedule")
        assert not faq.matches_search("pricing")

    def test_to_dict(self):
        """Test dictionary conversion"""
        faq = EnhancedFAQItem(
            question="Q",
            answer="A",
            category=FAQCategory.GENERAL.value,
            tags=["test"]
        )

        faq_dict = faq.to_dict()

        assert isinstance(faq_dict, dict)
        assert faq_dict["question"] == "Q"
        assert faq_dict["answer"] == "A"
        assert faq_dict["category"] == "general"

    def test_to_legacy_format(self):
        """Test legacy format conversion"""
        faq = EnhancedFAQItem(
            question="Q",
            answer="A",
            category=FAQCategory.PRODUCTS.value,
            tags=["tag1"]
        )

        legacy = faq.to_legacy_format()

        assert legacy == {"question": "Q", "answer": "A"}
        assert "category" not in legacy
        assert "tags" not in legacy

    def test_validation_no_question(self):
        """Test validation requires question"""
        with pytest.raises(ValueError, match="question is required"):
            EnhancedFAQItem(question="", answer="A")

    def test_validation_no_answer(self):
        """Test validation requires answer"""
        with pytest.raises(ValueError, match="answer is required"):
            EnhancedFAQItem(question="Q", answer="")


@pytest.mark.unit
class TestFAQManager:
    """Test FAQManager functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = FAQManager()

    def test_initialization(self):
        """Test manager initialization"""
        assert isinstance(self.manager.faqs, list)
        assert len(self.manager.faqs) == 0

    def test_add_single_faq(self):
        """Test adding a single FAQ"""
        faq = EnhancedFAQItem(question="Q", answer="A")
        self.manager.add_faq(faq)

        assert len(self.manager.faqs) == 1
        assert self.manager.faqs[0].question == "Q"

    def test_add_multiple_faqs(self):
        """Test adding multiple FAQs"""
        faqs = [
            EnhancedFAQItem(question="Q1", answer="A1"),
            EnhancedFAQItem(question="Q2", answer="A2"),
            EnhancedFAQItem(question="Q3", answer="A3")
        ]

        self.manager.add_faqs(faqs)

        assert len(self.manager.faqs) == 3

    def test_remove_faq(self):
        """Test removing FAQ by question"""
        faq1 = EnhancedFAQItem(question="Q1", answer="A1")
        faq2 = EnhancedFAQItem(question="Q2", answer="A2")

        self.manager.add_faqs([faq1, faq2])

        result = self.manager.remove_faq("Q1")

        assert result is True
        assert len(self.manager.faqs) == 1
        assert self.manager.faqs[0].question == "Q2"

    def test_remove_nonexistent_faq(self):
        """Test removing FAQ that doesn't exist"""
        result = self.manager.remove_faq("Nonexistent")

        assert result is False

    def test_get_faq_by_question(self):
        """Test retrieving FAQ by question"""
        faq = EnhancedFAQItem(question="Test Q", answer="Test A")
        self.manager.add_faq(faq)

        result = self.manager.get_faq_by_question("Test Q")

        assert result is not None
        assert result.question == "Test Q"

    def test_get_nonexistent_faq(self):
        """Test retrieving nonexistent FAQ"""
        result = self.manager.get_faq_by_question("Nonexistent")

        assert result is None

    def test_search_by_keyword(self):
        """Test searching by keyword"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="What are shipping costs?", answer="Free over $50"),
            EnhancedFAQItem(question="How long does shipping take?", answer="5-7 days"),
            EnhancedFAQItem(question="What is your return policy?", answer="30 days")
        ])

        results = self.manager.search(search_term="shipping")

        assert len(results) == 2

    def test_search_by_category(self):
        """Test filtering by category"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", category=FAQCategory.GENERAL.value),
            EnhancedFAQItem(question="Q2", answer="A2", category=FAQCategory.SHIPPING.value),
            EnhancedFAQItem(question="Q3", answer="A3", category=FAQCategory.SHIPPING.value)
        ])

        results = self.manager.search(category=FAQCategory.SHIPPING.value)

        assert len(results) == 2

    def test_search_by_tags(self):
        """Test filtering by tags"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", tags=["tag1", "tag2"]),
            EnhancedFAQItem(question="Q2", answer="A2", tags=["tag2", "tag3"]),
            EnhancedFAQItem(question="Q3", answer="A3", tags=["tag3", "tag4"])
        ])

        results = self.manager.search(tags=["tag2"])

        assert len(results) == 2

    def test_search_active_only(self):
        """Test filtering by active status"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", active=True),
            EnhancedFAQItem(question="Q2", answer="A2", active=False),
            EnhancedFAQItem(question="Q3", answer="A3", active=True)
        ])

        results = self.manager.search(active_only=True)

        assert len(results) == 2

    def test_get_by_category(self):
        """Test getting FAQs by category"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", category=FAQCategory.PRODUCTS.value),
            EnhancedFAQItem(question="Q2", answer="A2", category=FAQCategory.PRODUCTS.value)
        ])

        results = self.manager.get_by_category(FAQCategory.PRODUCTS.value)

        assert len(results) == 2

    def test_get_by_city(self):
        """Test getting FAQs by city"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", city_name="Orlando"),
            EnhancedFAQItem(question="Q2", answer="A2", city_name="Miami"),
            EnhancedFAQItem(question="Q3", answer="A3", city_name="Orlando")
        ])

        results = self.manager.get_by_city("Orlando")

        assert len(results) == 2

    def test_get_categories(self):
        """Test getting all categories"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", category=FAQCategory.GENERAL.value),
            EnhancedFAQItem(question="Q2", answer="A2", category=FAQCategory.SHIPPING.value),
            EnhancedFAQItem(question="Q3", answer="A3", category=FAQCategory.GENERAL.value)
        ])

        categories = self.manager.get_categories()

        assert len(categories) == 2
        assert FAQCategory.GENERAL.value in categories
        assert FAQCategory.SHIPPING.value in categories

    def test_get_all_tags(self):
        """Test getting all tags"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", tags=["tag1", "tag2"]),
            EnhancedFAQItem(question="Q2", answer="A2", tags=["tag2", "tag3"])
        ])

        tags = self.manager.get_all_tags()

        assert len(tags) == 3
        assert "tag1" in tags
        assert "tag2" in tags
        assert "tag3" in tags

    def test_get_statistics(self):
        """Test statistics generation"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", category=FAQCategory.GENERAL.value, active=True),
            EnhancedFAQItem(question="Q2", answer="A2", category=FAQCategory.GENERAL.value, active=False),
            EnhancedFAQItem(question="Q3", answer="A3", category=FAQCategory.SHIPPING.value,
                            city_name="Orlando")
        ])

        stats = self.manager.get_statistics()

        assert stats["total_faqs"] == 3
        assert stats["active_faqs"] == 2
        assert stats["inactive_faqs"] == 1
        assert stats["categories"]["general"] == 1
        assert stats["categories"]["shipping"] == 1
        assert stats["cities"]["Orlando"] == 1

    def test_clear(self):
        """Test clearing all FAQs"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1"),
            EnhancedFAQItem(question="Q2", answer="A2")
        ])

        self.manager.clear()

        assert len(self.manager.faqs) == 0


@pytest.mark.unit
class TestFAQManagerCSV:
    """Test CSV import/export functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = FAQManager()

    def test_export_to_csv(self):
        """Test exporting FAQs to CSV"""
        self.manager.add_faqs([
            EnhancedFAQItem(
                question="Q1",
                answer="A1",
                category=FAQCategory.GENERAL.value,
                tags=["tag1", "tag2"]
            ),
            EnhancedFAQItem(
                question="Q2",
                answer="A2",
                category=FAQCategory.SHIPPING.value
            )
        ])

        with TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test.csv"
            count = self.manager.export_to_csv(csv_path)

            assert count == 2
            assert csv_path.exists()

            # Verify CSV contents
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                assert len(rows) == 2
                assert rows[0]["question"] == "Q1"
                assert rows[0]["category"] == "general"
                assert "tag1" in rows[0]["tags"]

    def test_import_from_csv(self):
        """Test importing FAQs from CSV"""
        with TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test.csv"

            # Create CSV file
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'question', 'answer', 'category', 'tags', 'priority', 'active'
                ])
                writer.writeheader()
                writer.writerow({
                    'question': 'Test Q',
                    'answer': 'Test A',
                    'category': 'products',
                    'tags': 'tag1,tag2',
                    'priority': '5',
                    'active': 'true'
                })

            # Import
            count = self.manager.import_from_csv(csv_path)

            assert count == 1
            assert len(self.manager.faqs) == 1
            assert self.manager.faqs[0].question == "Test Q"
            assert self.manager.faqs[0].category == "products"
            assert len(self.manager.faqs[0].tags) == 2

    def test_export_active_only(self):
        """Test exporting only active FAQs"""
        self.manager.add_faqs([
            EnhancedFAQItem(question="Q1", answer="A1", active=True),
            EnhancedFAQItem(question="Q2", answer="A2", active=False)
        ])

        with TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test.csv"
            count = self.manager.export_to_csv(csv_path, active_only=True)

            assert count == 1


@pytest.mark.unit
class TestFAQManagerJSON:
    """Test JSON import/export functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = FAQManager()

    def test_export_to_json(self):
        """Test exporting FAQs to JSON"""
        self.manager.add_faqs([
            EnhancedFAQItem(
                question="Q1",
                answer="A1",
                category=FAQCategory.GENERAL.value,
                tags=["tag1"]
            )
        ])

        with TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "test.json"
            count = self.manager.export_to_json(json_path)

            assert count == 1
            assert json_path.exists()

            # Verify JSON contents
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                assert isinstance(data, list)
                assert len(data) == 1
                assert data[0]["question"] == "Q1"
                assert data[0]["category"] == "general"

    def test_import_from_json(self):
        """Test importing FAQs from JSON"""
        with TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "test.json"

            # Create JSON file
            data = [
                {
                    "question": "Test Q",
                    "answer": "Test A",
                    "category": "shipping",
                    "tags": ["tag1", "tag2"],
                    "priority": 5,
                    "active": True
                }
            ]

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)

            # Import
            count = self.manager.import_from_json(json_path)

            assert count == 1
            assert len(self.manager.faqs) == 1
            assert self.manager.faqs[0].question == "Test Q"

    def test_export_pretty_json(self):
        """Test pretty-printed JSON export"""
        self.manager.add_faq(EnhancedFAQItem(question="Q", answer="A"))

        with TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "test.json"
            self.manager.export_to_json(json_path, pretty=True)

            # Check that JSON is pretty-printed (has indentation)
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "\n" in content  # Has line breaks


@pytest.mark.unit
class TestFAQLegacyExport:
    """Test legacy format export"""

    def test_legacy_export(self):
        """Test exporting to legacy format"""
        manager = FAQManager()

        manager.add_faqs([
            EnhancedFAQItem(
                question="Q1",
                answer="A1",
                category=FAQCategory.GENERAL.value,
                tags=["tag1"],
                active=True
            ),
            EnhancedFAQItem(
                question="Q2",
                answer="A2",
                active=False  # Should not be exported
            )
        ])

        legacy = manager.export_to_legacy_format()

        assert len(legacy) == 1  # Only active
        assert legacy[0] == {"question": "Q1", "answer": "A1"}
        assert "category" not in legacy[0]
        assert "tags" not in legacy[0]
