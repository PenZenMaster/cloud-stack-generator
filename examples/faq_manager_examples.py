"""
FAQ Manager Usage Examples
Demonstrates bulk import/export, search, and category management

Run this file to see FAQ management in action:
    python examples/faq_manager_examples.py
"""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.content.faq_manager import (
    FAQManager,
    EnhancedFAQItem,
    FAQCategory
)


# Example 1: Creating and managing FAQs
def example_basic_faq_management():
    """Basic FAQ creation and management"""
    print("\n=== Example 1: Basic FAQ Management ===\n")

    manager = FAQManager()

    # Add individual FAQs
    faq1 = EnhancedFAQItem(
        question="What are your business hours?",
        answer="We are open Monday-Friday 9AM-5PM EST.",
        category=FAQCategory.GENERAL.value,
        tags=["hours", "contact", "availability"],
        priority=10
    )

    faq2 = EnhancedFAQItem(
        question="Do you offer free shipping?",
        answer="Yes, we offer free shipping on orders over $50.",
        category=FAQCategory.SHIPPING.value,
        tags=["shipping", "delivery", "cost"],
        priority=8
    )

    faq3 = EnhancedFAQItem(
        question="What is your return policy?",
        answer="We accept returns within 30 days of purchase with original packaging.",
        category=FAQCategory.RETURNS.value,
        tags=["returns", "refund", "policy"],
        priority=9
    )

    manager.add_faqs([faq1, faq2, faq3])

    print(f"Total FAQs: {len(manager.faqs)}")
    print(f"Categories: {manager.get_categories()}")
    print(f"All tags: {manager.get_all_tags()}")


# Example 2: Searching and filtering
def example_search_and_filter():
    """Demonstrate search and filter capabilities"""
    print("\n=== Example 2: Search and Filter ===\n")

    manager = FAQManager()

    # Add sample FAQs
    sample_faqs = [
        EnhancedFAQItem(
            question="How do I track my order?",
            answer="You can track your order using the tracking number sent to your email.",
            category=FAQCategory.SHIPPING.value,
            tags=["shipping", "tracking", "order"]
        ),
        EnhancedFAQItem(
            question="What payment methods do you accept?",
            answer="We accept Visa, Mastercard, American Express, and PayPal.",
            category=FAQCategory.GENERAL.value,
            tags=["payment", "billing", "credit card"]
        ),
        EnhancedFAQItem(
            question="How long does shipping take?",
            answer="Standard shipping takes 5-7 business days.",
            category=FAQCategory.SHIPPING.value,
            tags=["shipping", "delivery", "timeline"]
        ),
        EnhancedFAQItem(
            question="Can I cancel my order?",
            answer="Orders can be cancelled within 24 hours of placement.",
            category=FAQCategory.GENERAL.value,
            tags=["order", "cancel", "policy"]
        )
    ]

    manager.add_faqs(sample_faqs)

    # Search by keyword
    print("Search for 'shipping':")
    results = manager.search(search_term="shipping")
    for faq in results:
        print(f"  Q: {faq.question}")

    # Filter by category
    print("\nAll shipping FAQs:")
    shipping_faqs = manager.get_by_category(FAQCategory.SHIPPING.value)
    for faq in shipping_faqs:
        print(f"  Q: {faq.question}")

    # Filter by tags
    print("\nFAQs with 'order' tag:")
    order_faqs = manager.search(tags=["order"])
    for faq in order_faqs:
        print(f"  Q: {faq.question}")


# Example 3: City-specific FAQs
def example_city_faqs():
    """Demonstrate city-specific FAQ management"""
    print("\n=== Example 3: City-Specific FAQs ===\n")

    manager = FAQManager()

    # Add city-specific FAQs
    orlando_faqs = [
        EnhancedFAQItem(
            question="Do you serve Orlando, FL?",
            answer="Yes, we provide services throughout Orlando and surrounding areas.",
            category=FAQCategory.LOCATION.value,
            tags=["location", "service area"],
            city_name="Orlando",
            state="FL"
        ),
        EnhancedFAQItem(
            question="What are the delivery times in Orlando?",
            answer="We deliver to Orlando within 24-48 hours.",
            category=FAQCategory.SHIPPING.value,
            tags=["delivery", "timeline"],
            city_name="Orlando",
            state="FL"
        )
    ]

    miami_faqs = [
        EnhancedFAQItem(
            question="Do you serve Miami, FL?",
            answer="Yes, we serve Miami and all of South Florida.",
            category=FAQCategory.LOCATION.value,
            tags=["location", "service area"],
            city_name="Miami",
            state="FL"
        )
    ]

    manager.add_faqs(orlando_faqs + miami_faqs)

    # Get FAQs for specific city
    print("Orlando FAQs:")
    for faq in manager.get_by_city("Orlando"):
        print(f"  Q: {faq.question}")
        print(f"  A: {faq.answer}\n")


# Example 4: Bulk import from CSV
def example_csv_import_export():
    """Demonstrate CSV import/export"""
    print("\n=== Example 4: CSV Import/Export ===\n")

    manager = FAQManager()

    # Create sample FAQs
    sample_faqs = [
        EnhancedFAQItem(
            question="What is your email address?",
            answer="You can reach us at info@example.com",
            category=FAQCategory.GENERAL.value,
            tags=["contact", "email"],
            priority=5
        ),
        EnhancedFAQItem(
            question="Do you offer bulk discounts?",
            answer="Yes, contact us for bulk pricing options.",
            category=FAQCategory.PRICING.value,
            tags=["pricing", "discount", "bulk"],
            priority=7
        ),
        EnhancedFAQItem(
            question="Are your products eco-friendly?",
            answer="Yes, all our products are made from sustainable materials.",
            category=FAQCategory.PRODUCTS.value,
            tags=["products", "eco-friendly", "sustainability"],
            priority=6
        )
    ]

    manager.add_faqs(sample_faqs)

    # Export to CSV
    with TemporaryDirectory() as temp_dir:
        csv_path = Path(temp_dir) / "faqs.csv"
        exported = manager.export_to_csv(csv_path)
        print(f"Exported {exported} FAQs to CSV")

        # Read the CSV file to show contents
        print("\nCSV Contents (first 5 lines):")
        with open(csv_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < 5:
                    print(f"  {line.strip()}")

        # Import from CSV (into new manager)
        new_manager = FAQManager()
        imported = new_manager.import_from_csv(csv_path)
        print(f"\nImported {imported} FAQs from CSV")


# Example 5: Bulk import from JSON
def example_json_import_export():
    """Demonstrate JSON import/export"""
    print("\n=== Example 5: JSON Import/Export ===\n")

    manager = FAQManager()

    # Add sample FAQs
    manager.add_faqs([
        EnhancedFAQItem(
            question="How do I reset my password?",
            answer="Click 'Forgot Password' on the login page.",
            category=FAQCategory.ACCOUNT.value,
            tags=["account", "password", "security"]
        ),
        EnhancedFAQItem(
            question="Is my data secure?",
            answer="Yes, we use industry-standard encryption.",
            category=FAQCategory.TECHNICAL.value,
            tags=["security", "privacy", "data"]
        )
    ])

    # Export to JSON
    with TemporaryDirectory() as temp_dir:
        json_path = Path(temp_dir) / "faqs.json"
        exported = manager.export_to_json(json_path, pretty=True)
        print(f"Exported {exported} FAQs to JSON")

        # Show JSON contents
        print("\nJSON Contents (preview):")
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:500] + "..." if len(content) > 500 else content)


# Example 6: Statistics and reporting
def example_statistics():
    """Demonstrate FAQ statistics"""
    print("\n=== Example 6: Statistics and Reporting ===\n")

    manager = FAQManager()

    # Add diverse FAQs
    manager.add_faqs([
        EnhancedFAQItem("Q1", "A1", category=FAQCategory.GENERAL.value, tags=["tag1"]),
        EnhancedFAQItem("Q2", "A2", category=FAQCategory.GENERAL.value, tags=["tag1", "tag2"]),
        EnhancedFAQItem("Q3", "A3", category=FAQCategory.PRODUCTS.value, tags=["tag2"]),
        EnhancedFAQItem("Q4", "A4", category=FAQCategory.SHIPPING.value, tags=["tag3"]),
        EnhancedFAQItem("Q5", "A5", category=FAQCategory.SHIPPING.value, active=False),
        EnhancedFAQItem("Q6", "A6", category=FAQCategory.LOCATION.value,
                        city_name="Orlando", state="FL"),
    ])

    # Get statistics
    stats = manager.get_statistics()

    print(f"Total FAQs: {stats['total_faqs']}")
    print(f"Active FAQs: {stats['active_faqs']}")
    print(f"Inactive FAQs: {stats['inactive_faqs']}")
    print("\nBy Category:")
    for category, count in stats['categories'].items():
        print(f"  {category}: {count}")
    print("\nBy City:")
    for city, count in stats['cities'].items():
        print(f"  {city}: {count}")
    print(f"\nTotal unique tags: {stats['total_tags']}")


# Example 7: Legacy format export
def example_legacy_export():
    """Demonstrate export to legacy format"""
    print("\n=== Example 7: Legacy Format Export ===\n")

    manager = FAQManager()

    # Add enhanced FAQs
    manager.add_faqs([
        EnhancedFAQItem(
            question="What is your phone number?",
            answer="Call us at (555) 123-4567",
            category=FAQCategory.GENERAL.value,
            tags=["contact", "phone"],
            priority=10
        ),
        EnhancedFAQItem(
            question="Do you have a showroom?",
            answer="Yes, visit us at 123 Main St.",
            category=FAQCategory.LOCATION.value,
            tags=["location", "showroom"],
            priority=8,
            active=False  # This won't be exported
        ),
        EnhancedFAQItem(
            question="What are your certifications?",
            answer="We are ISO 9001 certified.",
            category=FAQCategory.GENERAL.value,
            tags=["certifications", "quality"],
            priority=5
        )
    ])

    # Export to legacy format (for config files)
    legacy_faqs = manager.export_to_legacy_format()

    print("Legacy format (question/answer only, active FAQs):")
    for faq in legacy_faqs:
        print(f"  - question: \"{faq['question']}\"")
        print(f"    answer: \"{faq['answer']}\"\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Cloud Stack Generator - FAQ Manager Examples")
    print("=" * 60)

    example_basic_faq_management()
    example_search_and_filter()
    example_city_faqs()
    example_csv_import_export()
    example_json_import_export()
    example_statistics()
    example_legacy_export()

    print("\n" + "=" * 60)
    print("FAQ Manager examples completed successfully!")
    print("=" * 60)
