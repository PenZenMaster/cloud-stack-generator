# location_page_generator.py

"""
Module/Script Name: location_page_generator.py

Description:
Generates fully optimized, HTML-based local service pages from CSV input.
Supports dynamic niche content, image/map embeds, and scalable WordPress deployment.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
2025-04-12

Last Modified Date:
2025-04-12

Comments:
- Version 1.03: Now loads Google Maps API key from .env file using dotenv.
"""

import os
import csv
import urllib.parse

# from slugify import slugify  # Optional external dependency
from jinja2 import Template  # Optional external dependency

# from dotenv import load_dotenv  # Optional external dependency

from src.core.utils.logger import get_logger

logger = get_logger(__name__)


# Simple slugify replacement
def slugify(text):
    """Simple slugify function"""
    text = text.lower()
    text = text.replace(" ", "-")
    text = text.replace(",", "")
    text = text.replace(" illinois", "")
    text = text.replace(" il", "")
    return text.strip("-")


# Load environment variables from .env
# load_dotenv()  # Optional external dependency
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

HTML_TEMPLATE = """
<!-- {{ location }} Location Page – {{ business_name }} -->

<h1>{{ page_title }}</h1>
<p>{{ intro_paragraph }}</p>

<a title="{{ image_attribution }}" href="{{ image_source_url }}" target="_blank" rel="noopener">
  <img width="100%" style="height:auto; margin: 20px 0;" src="{{ image_embed_url }}" alt="{{ page_title }}">
</a>

<h2>Why Choose {{ page_title }} from {{ business_name }}?</h2>
<p>{{ why_us_paragraph }}</p>

<h2>Explore {{ location }} While We Work</h2>
<p>{{ local_paragraph }}</p>
<iframe src="{{ map_embed_url }}" width="100%" height="400" style="border:0;" allowfullscreen loading="lazy"></iframe>

<h2>Driving Directions to Our Office from {{ location }}</h2>
<p>We're located at {{ hq_address }}.</p>
<iframe src="{{ directions_embed_url }}" width="100%" height="400" style="border:0;" allowfullscreen loading="lazy"></iframe>

<h2>Exterior Painting Services We Offer in {{ location }}</h2>
<ul>
  {% for service in services %}
  <li>{{ service }}</li>
  {% endfor %}
</ul>

<h2>Request a Free Quote Today</h2>
<p>{{ cta_paragraph }}</p>
<p><strong>Contact Us:</strong><br>
Phone: <a href="tel:{{ phone }}">{{ phone }}</a><br>
Email: <a href="mailto:{{ email }}">{{ email }}</a><br>
Address: <a href="{{ hq_map_url }}" target="_blank">{{ hq_address }}</a></p>
"""


def parse_services(service_str):
    return [s.strip() for s in service_str.split("|") if s.strip()]


def build_google_map_embed(location):
    q = urllib.parse.quote(location)
    return f"https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAPS_API_KEY}&q={q}"


def build_google_directions_embed(start, end):
    origin = urllib.parse.quote(start)
    destination = urllib.parse.quote(end)
    return f"https://www.google.com/maps/embed/v1/directions?key={GOOGLE_MAPS_API_KEY}&origin={origin}&destination={destination}"


def build_wikipedia_image_embed(city):
    safe_city = city.split(",")[0].strip().replace(" ", "_")
    image_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/{safe_city}.jpg/1280px-{safe_city}.jpg"
    source_url = f"https://commons.wikimedia.org/wiki/File:{safe_city}.jpg"
    return image_url, source_url, f"Wikimedia Commons, {safe_city}.jpg"


def generate_location_page(row):
    focus_keyword = row["Primary Focus Keyword"]
    location = row["Location (City,State)"]
    phone = row["Phone"]
    email = row["Email"]
    business_name = row["Business Name"]
    hq_address = row["HQ Address"]
    service_str = row.get("Service List", "")
    services = parse_services(service_str) or [
        "Full exterior repaints",
        "Trim, fascia, shutters, and doors",
        "Deck and porch painting or staining",
        "Color consultation",
        "Historic restoration or modern upgrades",
    ]

    page_title = f"{focus_keyword} in {location}"
    slug = slugify(location)

    map_embed_url = build_google_map_embed(location)
    directions_embed_url = build_google_directions_embed(location, hq_address)
    image_embed_url, image_source_url, image_attribution = build_wikipedia_image_embed(
        location
    )

    template = Template(HTML_TEMPLATE)
    html_output = template.render(
        page_title=page_title,
        business_name=business_name,
        location=location,
        phone=phone,
        email=email,
        hq_address=hq_address,
        hq_map_url="https://goo.gl/maps/kD8T7YAkzEv6GQbC8",
        map_embed_url=map_embed_url,
        directions_embed_url=directions_embed_url,
        image_embed_url=image_embed_url,
        image_source_url=image_source_url,
        image_attribution=image_attribution,
        intro_paragraph=f"Professional {focus_keyword.lower()} with guaranteed reliability and clean, lasting results.",
        why_us_paragraph="Our proven process includes power washing, priming, and expert application using top-tier materials.",
        local_paragraph=f"Explore the best of {location} while we work—grab coffee, visit parks, and come back to a refreshed home exterior.",
        cta_paragraph=f"Looking for {focus_keyword.lower()} you can trust in {location}? Let's talk!",
        services=services,
    )

    output_path = os.path.join("output", f"{slug}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    logger.info(f"Generated: {output_path}")


def run():
    with open("input/locations.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            generate_location_page(row)


if __name__ == "__main__":
    run()
