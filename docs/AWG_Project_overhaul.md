Cloud Site Content Transformation Guide
Converting a Duplicate Cloud Site into a Legitimate Resource/Guide Site
Current Site Audit Summary
Domain: d1u73jtil3oxr6.cloudfront.net
Pages: ~100+ (1 homepage, 14 service pages, 72+ product pages, 2 location pages, FAQ, Contact, About, Privacy Policy)
Current problem: Near-exact duplicate of overheaddoorjoliet.com — same branding, same product descriptions, same company info. Google sees this as a manufactured link scheme, not an independent resource.

PHASE 1: Identity & Branding Overhaul
What to Change in the Generator Tool
The tool currently clones the money site's identity onto the cloud site. Instead, the generator needs to create a distinct brand identity for each cloud site — one that positions it as an independent educational resource, not a business storefront.

1.1 — Site Name & Branding
Current (Clone)	Target (Resource Site)
"Overhead Door Company of Joliet"	A topical resource name, e.g., "Commercial Door Guide" or "Illinois Loading Dock Resource Center" or "[Region] Commercial Door Advisor"
Company logo in header	Resource site logo (no client branding)
Phone number (815-725-6077)	No direct client phone number — site is educational, not a storefront
"Get Your Custom Quote Today" CTAs	Educational CTAs: "Read the Full Guide," "Download the Buyer's Checklist," "Compare Door Types"
Generator change: Accept a site_name and site_brand parameter separate from the client's business name. The brand should convey "educational resource" not "service provider."

1.2 — Domain
Current	Target
d1u73jtil3oxr6.cloudfront.net	A real registered domain, e.g., commercialdoorguide.com or ildockresource.com
Generator change: Deploy to a custom domain (even if still hosted on CloudFront/S3 behind it). The CDN subdomain must never be the public-facing URL.

1.3 — About Page
Current	Target
Company history ("Since 1978...")	Resource site mission: "This site was created to help facility managers, building owners, and contractors make informed decisions about commercial and industrial door systems."
Company team/credentials	Editorial perspective: who writes/reviews the content (can be generic, e.g., "Our editorial team includes commercial construction professionals with 20+ years of experience")
PHASE 2: Content Type Transformation
This is the most critical change. The current site has two content types that are both problematic:

Service pages — duplicate descriptions of the client's services

Product pages — duplicate spec sheets for Overhead Door™ products

Both need to be replaced with original educational content that happens to be topically relevant.

2.1 — Replace Service Pages with "How-To" / "Guide" Content
The generator currently creates 14 service pages that read like sales copy. These need to become educational guides written from a third-party perspective.

Current Service Page	Replace With
Commercial Door Installation	"Complete Guide to Commercial Garage Door Installation: What to Expect"
High-Speed Door Installation	"High-Speed Door Installation: Requirements, Timeline, and What to Ask Your Installer"
Loading Dock Equipment Installation	"Loading Dock Equipment Installation Checklist: ANSI MH30.1-2022 Compliance Guide"
Commercial Garage Door Repair	"Commercial Garage Door Troubleshooting: When to Repair vs. Replace"
Commercial Opener Repair & Replacement	"Commercial Garage Door Opener Brands Compared: Chamberlain vs. LiftMaster vs. Genie"
High-Speed Door Repair	"High-Speed Door Common Failures: Diagnosing Curtain, Track, and Sensor Issues"
Loading Dock Equipment Repair	"Loading Dock Safety Audit: A Facility Manager's Annual Checklist"
Keypad Installation & Programming	"Commercial Access Control Systems: Keypads, Fobs, and Smart Locks Compared"
Commercial Man Door Service	"Pedestrian Access Doors in Commercial Facilities: Code Requirements and Best Practices"
Commercial Garage Door Maintenance	"Commercial Garage Door Maintenance Schedule: Frequency by Door Type and Usage"
Planned Maintenance Program	"How to Build a Preventive Maintenance Program for Commercial Doors and Docks"
Fire Door Drop Testing & Compliance	"Fire Door Drop Testing: NFPA-80 Requirements, UL/FM Standards, and Annual Compliance Guide"
On-Site / Phone Consultation	"How to Evaluate a Commercial Garage Door Contractor: 10 Questions to Ask"
Commercial Garage Door Services (overview)	"The Complete Guide to Commercial & Industrial Garage Door Systems" (pillar page)
Key content principles for the generator:

Write from third-party educational perspective ("When choosing a commercial door installer, look for...") not first-person sales ("We install...")

Include data, standards references, and practical checklists — things a facility manager would bookmark

Reference multiple brands and options, not exclusively Overhead Door™ products

Include the client's business as ONE recommendation among several, or in a contextual mention like: "For professional installation in the Joliet, IL area, Overhead Door Company of Joliet has served commercial clients since 1978."

2.2 — Replace Product Pages with Comparison/Buyer's Guide Content
The current 72+ product pages are individual spec sheets duplicated from manufacturer content. This is the biggest red flag — Google sees 72 pages of copied spec data.

Option A: Consolidate into Buyer's Guide Categories (Recommended)

Instead of 72 individual product pages, create ~8-12 comprehensive comparison guides:

Replace These Product Pages	With This Guide
8 Thermacore® models (591-850)	"Insulated Commercial Steel Doors: R-Value Comparison Guide and Selection Matrix"
8 Standard Sectional Steel models (416-432)	"Non-Insulated vs. Insulated Sectional Steel Doors: Which Does Your Facility Need?"
4 Aluminum Glass models (511-522)	"Aluminum Glass Garage Doors for Commercial Use: Visibility, Light, and Aesthetics Guide"
10 WindStorm™ models (421-525)	"Wind-Rated Commercial Doors: Understanding Design Pressure and Code Requirements"
12 Rolling Steel models (600-627)	"Rolling Steel vs. Sectional: Choosing the Right Commercial Door Configuration"
5 Fire-Rated models (630-635)	"Fire-Rated Door Requirements: UL Ratings, FM Approval, and NFPA-80 Compliance Explained"
7 Fire-Rated Counter models (640-662)	"Fire-Rated Counter Doors: Comparing Options for Food Service, Retail, and Institutional Use"
10 Security Grille models (670-683)	"Commercial Security Grilles: Upward Coiling vs. Side Folding — Visibility, Airflow, and Security Trade-offs"
6 Counter Door models (650-665)	"Rolling Counter Doors: Material Options from Steel to Wood for Every Application"
3 Rolling Sheet models (770SS-790CW)	"Rolling Sheet Doors: Light-Duty to Wind-Rated — Self-Storage and Commercial Applications"
7 High-Speed models (990-999)	"High-Speed Commercial Doors: Fabric vs. Rubber vs. Metal — Speed, Durability, and ROI Compared"
9 Loading Dock Equipment items	"Loading Dock Equipment Buyer's Guide: Levelers, Restraints, Seals, and Shelters Explained"
Key principles for product content:

Comparison format — tables comparing specs across models, not single-product sales pages

Include competing brands — mention Wayne Dalton, Clopay, Amarr, Rytec, Assa Abloy alongside Overhead Door™

Add decision-making frameworks — "Choose Model X if your facility needs [criterion], choose Model Y if..."

Original analysis — R-value efficiency calculations, total cost of ownership estimates, lifecycle comparisons

Cite manufacturer sources — link to actual Overhead Door™ product pages and other manufacturer pages as references

Option B: Keep Individual Pages but Make Them Reviews (Higher effort)

Each product page becomes a detailed, original review:

Pros/cons from an installer's or facility manager's perspective

Comparison to competing products in the same category

"Best for" and "Not ideal for" sections

Real-world application examples

Independently researched content, not copy-pasted spec sheets

2.3 — Replace Location Pages with Local Resource Content
Current	Target
"Joliet, Illinois" (service area sales page)	"Commercial Building Resources in Joliet, IL: Permits, Contractors, and Code Requirements"
"Aurora, Illinois" (service area sales page)	"Aurora, IL Commercial Construction Guide: Zoning, Inspections, and Approved Contractors"
These should be genuinely useful local resource pages that a building owner would actually use — links to city permitting offices, building code references, local contractor directories (including but not limited to the client).

PHASE 3: New Content the Generator Should Add
The current tool doesn't generate these, but they're what make a resource site earn links and traffic on its own:

3.1 — Original Educational Content (New Section)
Add a /guides/ or /resources/ section with content that doesn't exist on the money site:

"Commercial Garage Door R-Value Calculator" — interactive tool where users input square footage, climate zone, and usage to get insulation recommendations

"NFPA-80 Fire Door Compliance Checklist (Printable PDF)" — downloadable resource

"Commercial Door Maintenance Cost Calculator" — estimate annual maintenance costs by door type and count

"Loading Dock Safety Standards Quick Reference" — ANSI MH30.1-2022 key requirements summarized

"Illinois Commercial Building Code Requirements for Overhead Doors" — state-specific code reference

"Energy Savings Calculator: Insulated vs. Non-Insulated Commercial Doors" — based on climate data for Will County/Joliet area

3.2 — Blog/Articles Section
A /blog/ or /articles/ section with ongoing original content:

Industry news and code updates

Case study formats (anonymized if needed): "How a Joliet Warehouse Reduced Energy Costs 30% with Insulated Rolling Doors"

Seasonal content: "Winterizing Your Loading Dock: A Pre-Season Checklist for Illinois Facilities"

Comparison articles: "Sectional Steel vs. Rolling Steel: 5 Factors That Determine Which Is Right for Your Facility"

PHASE 4: Linking Structure Changes
4.1 — Outbound Links (FROM the Cloud Site)
Current Pattern	Target Pattern
Links only to overheaddoorjoliet.com	Links to multiple relevant resources
Footer link: "Visit Main Website" pointing to money site	Remove or replace with a natural contextual mention
The generator should create outbound links to:

Multiple authoritative sources: Overhead Door™ manufacturer (overheaddoor.com), DASMA (Door & Access Systems Manufacturers Association), NFPA, ANSI, IDA (International Door Association)

The client — as ONE of several recommended resources, not the sole destination

Other local businesses — complementary trades (electricians, general contractors, HVAC companies in the service area)

Government resources — city permitting pages, state building code references

Target ratio: No more than 15-20% of outbound links should point to the money site. The rest should point to genuinely useful third-party resources.

4.2 — Internal Links
The site should have a logical hub-and-spoke structure:

Pillar/guide pages link to related sub-guides

Sub-guides link back to pillar pages and to each other

This creates topical authority clusters that Google recognizes as genuine site architecture

4.3 — Link to Money Site Contextually
Instead of a footer link or sitewide link, the money site should only be referenced where contextually relevant:

Bad (current):

Footer: "Visit Main Website → overheaddoorjoliet.com"

Good (target):

Within the "How to Evaluate a Commercial Garage Door Contractor" guide:
"In the greater Joliet, Illinois area, established providers include Overhead Door Company of Joliet, which has served commercial and industrial clients since 1978, and [other local contractor]."

PHASE 5: Technical Changes for the Generator
5.1 — Meta Tags & Schema
Element	Current	Target
<title>	"Overhead Door Company of Joliet - Your Local Garage Door Experts"	"[Resource Site Name] - Commercial Door Guides & Resources"
<meta description>	Sales copy about the company	Educational description about what the resource offers
Schema markup	None (or company LocalBusiness schema)	Article, HowTo, FAQPage schema for guide content; NO LocalBusiness schema (it's not a business)
<meta name="robots">	Index, follow	Consider noindex for pages that don't have enough unique content to stand alone
Canonical tags	None or self-referencing	Ensure no canonical pointing to the money site (that would defeat the purpose)
5.2 — Template Design
The site template should look visually distinct from the money site:

Different color scheme (currently uses the same red/white as overheaddoorjoliet.com)

Different layout structure

Resource/guide-focused design (table of contents, comparison tables, downloadable resources)

No QR code in the hero pointing to the money site

5.3 — Content Generation Rules
If the tool uses AI/templates to generate content, build in these guardrails:

No first-person company voice — never "We install," "Our team," "Call us today"

No duplicate content — content must not appear on the money site or any other cloud site

Include competing brands/options — at least 2-3 alternatives for any product or service mentioned

Cite real standards and codes — NFPA, ANSI, UL, FM, IECC with actual section numbers

Include original analysis — cost comparisons, performance calculations, decision frameworks

Natural link placement — maximum 1-2 contextual links to the money site per page, not sitewide/footer links

Summary: Minimum Viable Changes
If you want to make the smallest set of changes that would move the needle most:

Must-Do (Non-Negotiable)
Custom domain — get off the CloudFront subdomain

Remove client branding — different name, logo, color scheme

Rewrite all content in third-person educational voice — no "we," no "our team," no "call us"

Consolidate 72 product pages into ~12 comparison guides — eliminate duplicate spec content

Diversify outbound links — link to multiple sources, not just the money site

Remove sitewide footer link to the money site

Should-Do (High Impact)
Add 5-10 original guide/resource pages that don't exist on the money site

Include competing brands in product comparisons

Add downloadable resources (checklists, PDFs, calculators)

Implement proper Article/HowTo schema markup

Nice-to-Have (Maximum Value)
Blog section with ongoing original content

Interactive tools (R-value calculator, cost estimator)

Local resource pages with links to city permits, code offices

Build the resource site's own backlink profile from third parties

The Bottom Line
The generator tool needs to shift from producing cloned storefronts to producing topical authority resource sites. The content should pass this test:

"Would this page be useful and worth visiting even if it never linked to the money site?"

If the answer is yes, it's a legitimate resource. If the answer is no, Google will eventually treat it as a link scheme.