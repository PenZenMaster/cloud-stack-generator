# What is a “Cloud Stack” site (in practice)?

A **fast, static microsite network** hosted on cloud/CDN properties (e.g., S3/CloudFront, GCS, Azure Blob, GitHub Pages, Google Sites, etc.) that:

* Establishes and reinforces the **brand/entity** with consistent NAP + SameAs.
* Publishes Service and or Product Pages with genuine value (not doorway pages).
* For strong georelevance select cities in the local area are build
* **Interlinks** pages and stacks to pass relevance and crawl paths back to the money site.

---

# Core architecture (the mental model)

```
[Brand Hub (Home)]
   ├── Services  Pillar
   │     ├── Service Page A
   │     ├── Service Page B
   │     └── Service Page C
   ├── Products  Pillar
   │     ├── Product Page A
   │     ├── Product Page B
   │     └── Product Page C
   ├── Cities Pillar
   │     ├── City Page: City-1
   │     │     └── City-1 Service Variants (optional)
   │     ├── City Page: City-2
   │     └── City Page: City-3
   ├── Case Studies/Projects (optional but powerful)
   ├── FAQ (global)
   └── Contact
```

**Linking rules of thumb**

* Hub → all pillars; nav exposes Services & Cities.
* Each **Service Page** links to: 1–2 sibling services, 2–3 relevant City Pages, FAQ, and **1 deep link** to the money site’s corresponding page.
* Each **City Page** links to: 1–2 primary service pages, 2 adjacent city pages (ring), FAQ, Contact, and **1 deep link** to the money site’s best match (service in that city, if it exists).
* **Footer**: brand NAP + SameAs + one “About” link to the money site. Avoid site-wide exact-match anchors.

---

# Page types & what they must contain

## 1) Brand Hub (Home)

Purpose: establish entity, topical scope, and send crawlers into your silos.

* 250–500 word brand intro + **E-E-A-T** signals (years in biz, licenses, awards).
* “We do X for Y” positioning + short **Services** overview.
* “Areas we serve” listing linking to **Cities Pillar**.
* Trust block: badges, brief testimonial, links to policies (Privacy/ToS) to look legit.
* **Schema**: `Organization` or `LocalBusiness` (if appropriate), `WebSite`, `BreadcrumbList`.
* **Links out** (SameAs): official social profiles, GBP, industry directories.

## 2) Services Pillar (index/overview)

Purpose: summarize offerings and pass equity to individual service pages.

* Short intro (100–200 words) + cards for each service (title, 50–80 word blurb).
* Internal links to service detail pages with **descriptive anchors** (no anchor stuffing).
* **Schema**: `ItemList` of services, `BreadcrumbList`.

## 3) Service Detail Pages (one per core service)

Purpose: rank for **“service + city”** variants when paired via interlinks; support conversions.

* 700–1,100 words **unique** content:

  * What it is, how it works, benefits, materials/tech specs, process steps, timelines.
  * 2–3 mini case blurbs (even hypothetical, but realistic).
  * “Works great with” cross-links (related services).
* Visuals: 2–4 optimized images (alt includes entity + topic; no keyword stuffing).
* **FAQ**: 4–6 Q\&As that match PAA intent.
* **CTA**: link to Contact and one **deep link** to the money site’s matching service.
* **Schema**: `Service` +`Product` + `FAQPage` + `BreadcrumbList`.

## 4) Cities Pillar (index/overview)

Purpose: connect Hub to each city page; give crawlers a clean city sitemap.

* Intro about coverage model + map image (static) if you’re SAB.
* Grid of **City Pages** (alphabetical or by hub proximity).
* **Schema**: `ItemList` of `City` pages, `BreadcrumbList`.

## 5) City Pages (local domination workhorses)

Purpose: rank for **“service in {City}”** and discovery variants.

* 800–1,200 words **per city** (minimum 40% unique vs. other cities):

  * City-specific intro (neighborhoods/landmarks), seasonal/local pain points.
  * “Top services we provide in {City}” (2–4 short sections linking to Service pages).
  * 1–2 **micro case studies**/before-after relevant to the city.
  * **Driving-direction style section** (text): how locals typically approach working with you (SAB? describe process and arrival times; don’t reveal hidden addresses).
  * Local resources/standards (link out sparingly to credible local sources).
* **FAQ**: 4–6 Q\&As specific to {City}.
* **Trust**: a testimonial from a nearby client (even if general, attribute to locale).
* **CTA**: contact + link to money site (corresponding city/service page if available).
* **Interlinks**: to 2 adjacent cities + 1–2 primary services.
* **Schema**: `LocalBusiness` (SAB flags if applicable) or `ProfessionalService`, `FAQPage`, `BreadcrumbList`. Include `areaServed` with city/region.

## 6) Case Studies / Projects (optional but potent)

* 400–800 words, problem → solution → outcome, with images.
* Link back to the **service** used and the **city**.
* **Schema**: `CreativeWork` or `CaseStudy`.

## 7) FAQ (global)

* 8–12 Q\&As spanning policy, timelines, warranties, pricing ranges.
* Link out to relevant service/city pages within answers.
* **Schema**: `FAQPage`.

## 8) Contact

* Form or mailto/tel links (static stacks often use mailto/tel).
* NAP (SAB: show phone/email; omit precise address if hidden on GBP).
* **Schema**: `ContactPage`.

---

# Interlinking patterns (make it systematic)

**On every Service Page:**

* Link to **2 sibling services** (contextual).
* Link to **3 priority City Pages** where that service is in demand.
* Link to **FAQ** item(s).
* Link once to **money site’s equivalent page** (use branded/neutral anchor).

**On every Product Page:**

* Link to **2 sibling services** (contextual).
* Link to **3 priority City Pages** where that service is in demand.
* Link to **FAQ** item(s).
* Link once to **money site’s equivalent page** (use branded/neutral anchor).

**On every City Page:**

* Link to **2 priority services**.
* Link to **2 adjacent city pages** (“nearby” ring structure).
* Link to **Contact** and **FAQ**.
* Link once to the **money site**, targeting the best match.

**Anchors mix (site-wide targets):**

* \~50% branded/URL/neutral (“Learn more”, “See details”, “BrandName”).
* \~30% partial-match (“custom roof vents in {City}”).
* \~20% topical entities (“copper dormers”, “chimney shroud fabrication”).

---

# Content & quality checklist (per page)

* **Originality**: ≥40% unique text vs. siblings; fresh examples and city facts.
* **Depth**: answer how/why/cost/risks/alternatives; include process steps.
* **Media**: 2–4 images (compressed, descriptive filenames, accurate alt); optional short video.
* **UX**: scannable headings (H2/H3), lists, short paragraphs, strong CTA.
* **Compliance**: Privacy/ToS pages present; no misleading claims; avoid doorway duplication.
* **Speed**: static hosting + CDN; lazy-load images; include width/height for CLS.
* **Indexing hygiene**: noindex thin stubs; unique titles/meta; descriptive slugs.

---

# Schema playbook (minimum viable)

* **Site-wide**: `WebSite`, `Organization`/`LocalBusiness` (SAB: `hasMap` can be a GBP share link; use `areaServed`).
* **Page-level**:

  * Services → `Service`
  * Cities → `LocalBusiness`/`ProfessionalService` with `areaServed` {City}
  * FAQ → `FAQPage`
  * Breadcrumbs → `BreadcrumbList`
* **Entity reinforcement**: `sameAs` to brand socials, GBP, authoritative profiles.
* **G-Sites note**: if JSON-LD is stripped, inject via GTM or link to a hosted JSON file and progressively enhance content to compensate.

---

# URL & file naming patterns

* Services: `/services/custom-roof-vents/`
* Cities index: `/locations/`
* City pages: `/locations/{city-slug}/` (avoid adding state in slug unless necessary)
* Images: `service-city-brand-keyword.jpg` (short, truthful)
* Keep **self-canonicals**; do **not** canonical to the money site (avoid doorway signals).

---

# City page unique-content framework (fast drafting)

For each {City}:

1. **Intro (120–180 words)**: City context, neighborhoods, seasonal issues.
2. **Top Services (3× 120–150 words)**: What’s most common in {City} + link to service.
3. **Mini Case (120–180 words)**: Problem → fix → outcome; mention a neighborhood/landmark.
4. **Process in {City} (100–150 words)**: Scheduling, lead time, arrival windows.
5. **FAQ (4–6 Q\&As)**: City-specific concerns (permits, weather, access).
6. **CTA + Trust**: Testimonial or rating snippet; contact options.
7. **Interlinks**: 2 adjacent cities, 1–2 services, FAQ.

---

# Avoid these pitfalls

* **Doorway duplication**: swapping only the city name. Add real, city-specific value.
* **Over-optimized anchors**: keep partial-match in check.
* Thin pages (<500 words), missing trust cues, or no policy pages.
* Linking every page directly to the money site with exact-match anchors (looks manipulative).

---

# Launch & QA checklist

* Titles/meta written for every page (distinct; include brand + entity verbs).
* H1 present, logical H2/H3 hierarchy.
* Internal links tested (no 404s), external links sparing and authoritative.
* Images compressed; CLS safe; LCP under control (static stack = advantage).
* Valid JSON-LD (test a sample).
* XML sitemap (if platform supports) or HTML index pages (Cities/Services).
* Robots: allow crawling unless a page is incomplete → `noindex`.

---

# Simple production SOP (hand this to the team)

1. Build the site skeleton (Hub, Services Pillar + pages, Cities Pillar + pages, FAQ, Contact).
2. Draft service pages first; publish with internal links.
3. Draft top 5–10 **City Pages** using the framework above (≥40% unique each).
4. Wire interlinks per rules (services ↔ cities; city ↔ adjacent cities; all ↔ FAQ/Contact).
5. Add schema; validate one service page + one city page.
6. Compress images; ship to cloud host/CDN; test speed & rendering.
7. Submit to GSC (if applicable) or drive discovery via links from known entities (GBP site, social profiles, existing properties).
8. Monitor indexing & queries; tune titles/meta; add 2–3 new city pages per week.


