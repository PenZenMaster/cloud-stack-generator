# AWG Startup Context

**Last Updated:** 2026-08-08
**Branch:** main
**Version:** 4.1.0
**Last Commit:** 75b225f - feat(seo): content uniqueness gate (core engine only)

---

## Last 3 Accomplishments

1. **4 critical/high SEO-risk issues closed (#33-36)** - fabricated Product ratings removed;
   stale canonical-URL doc corrected; scaled template-fallback content gated after redirecting
   from the issue's dead-code premise to the real mechanism; LocalBusiness+NAP schema
   restricted to `main_site` only.

2. **Anchor-text rotation engine core shipped (#37, 4c8a98e)** - `AnchorProfileConfig` +
   `AnchorSelector` (seeded, drift-correcting, no intra-page repeats, safety ceiling), wired
   into both page generators, all 6 hardcoded anchors replaced. Core-engine-only per explicit
   user scoping; UI editor tab and `anchor_report.json` deferred, issue left OPEN with scope
   documented in a comment. Also fixed a real blocker found along the way: the backlink CTA
   section in the live city template never rendered for any city page at all.

3. **Content uniqueness gate core shipped (#38, 75b225f)** - `UniquenessGate` (5-word
   shingling + MinHash + LSH banding, near-linear scoring), `ContentQualityConfig`, wired as
   a pre-publish check into both the GUI (`PageGenerator`) and CLI (`WebsiteOrchestrator`)
   production paths, strengthened the AI city-page prompt for per-city differentiation. Same
   core-engine-only scoping as #37; embeddings, money-site live comparison, regeneration
   loop, and report/UI dialog deferred and documented in a comment.

---

## Next 3 Priorities

1. **#39 - Footprint diversifier** - bucket naming, template skins, CSS prefixes, provider
   rotation. Feature-sized; ask the user for scope before diving in, same as #37/#38.

2. **#40 - GSC indexing pipeline** - property provisioning, sitemap submit, coverage tracking.
   Also feature-sized; likely needs a Google API credentials/scoping discussion up front.

3. **Revisit deferred scope on #37/#38, or move to the template-system epic (#41-62)** -
   once #39/#40 are triaged. #37/#38 both have UI editor/dialog work and other subsystems
   (embeddings, external fetching, regeneration loops) still open on their original issues.

All four issues (#37-40) came from the same 2026-08-07 risk assessment (see
`docs/cloud-stack-generator-assessment.md`, still untracked).

---

## Current State

**Git:**
- Branch: main
- Version: 4.1.0
- Last commit: 75b225f (pushed as part of this checkpoint)
- Working tree: `.claude/settings.local.json` modified (local, not committed);
  `docs/cloud-stack-generator-assessment.md` and `docs/qa1.png` untracked (source assessment
  doc + screenshot, left as-is - user hasn't said whether to commit them)

**Tests:**
- Total: 1009 PASSING, 83 pre-existing failures (unchanged), 6 skipped, 1 pre-existing error
- No new failures from any of #33-38
- Full-suite run times were erratic across this and the prior session (118s to as much as
  4885s/81min across identical runs, no code changes between) - system load from stacked
  background bash processes, not a code issue. Result counts matched exactly across fast and
  slow runs, so slow runs were still trusted as valid pass/fail signals

**Blockers:**
- User still needs AWS S3/CloudFront setup for localgaragedoorcompanyreviews.com before the
  Resource Site + Providers QA from an earlier session (carried over, untouched)

**Known Issues:**
- Camphouse Country Landscaping (SAB) GBP unresolved - try direct Place ID
- Cost display shows $0.0000 instead of actual cost - LOW priority
- Business tab "Generate with AI" buttons use OpenAI (not Claude) - works if OPENAI_API_KEY set
- `enhanced_city_page_generator.py` confirmed dead code (never instantiated anywhere) -
  genuine cleanup is issue #44's scope
- `google_business_profile` field in `generate_yaml_dict()` writes the raw dataclass object
  instead of a plain dict, so a full save-to-disk-and-reload round trip crashes on
  `yaml.safe_load`. Pre-existing, `test_meta_tags_feature.py::test_save_load_roundtrip_
  preserves_meta_tags` already covers it as a known failure - small fix whenever someone's
  in that file (config round-trip tests for #37/#38 route around it via
  generate_yaml_dict()->parse_yaml_dict() instead of the disk cycle)

---

## Key Context Notes

1. **Resource site domain** goes in Business Info tab > Website field (not "Domain" —
   the UI label is "Website" but the underlying key is `domain`). Main Site URL on
   Cloud Deploy tab is for backlink sites only — leave blank for resource sites.

2. **Providers workflow** - Each promoted client is added as a Provider (Providers tab).
   External followed link lives on `providers/{slug}.html`. Topic guide pages link
   internally to the profile (not directly to client domain). `_pick_provider()` matches
   provider specialties to topic keywords to inject featured CTA automatically.

3. **AWS setup sequence** - ACM cert must be in us-east-1. S3 uses OAC (not public
   access). Bucket policy comes from CloudFront banner after distribution creation.
   Cloud Deploy tab needs: S3 bucket name, AWS region, CloudFront distribution ID.

4. **Anchor-text engine (#37)** - `src/core/generators/content/anchor_selector.py`.
   `build_anchor_selector(config)` resolves identity per site_type: client's own business for
   backlink_site, `resource_site.money_site_name`/`money_site_url` for resource sites.
   Template usage: `{{ anchor(slot='footer') }}` or `{{ anchor(slot='body_contextual') }}`.

5. **Content uniqueness gate (#38)** - `src/core/quality/uniqueness_gate.py`.
   `UniquenessGate.add_page(id, html)` then `.check()` raises `UniquenessGateError` on block,
   or returns a `UniquenessReport` with warned-but-not-blocked pages. Wired into both
   `PageGenerator._check_content_uniqueness()` and `WebsiteOrchestrator._check_content_
   uniqueness()` - if extending either production path's generation flow, remember this runs
   right before the method returns/finalizes, reading back every `.html` path already in the
   generated-files list.

6. **When scoping a feature-sized issue** (#37/#38 were the template) - ask the user upfront
   how much to build (core engine vs full UI vs everything) rather than assuming. Also worth
   checking whether the issue's named root-cause file is actually in the live render path
   before fixing it - #35 named dead code, and the real fix was elsewhere. And double-check
   your own test fixtures are realistic before trusting a failing test as an algorithm bug -
   #38's first fixture understated real similarity due to unrealistic proportions, not a bug
   in the similarity engine itself.

---

## Quick Reference

**Run tests:**
```cmd
python -m pytest -q --ignore=tests/unit/test_ai_content_service.py
```

**Theme presets location:**
- `src/core/config/theme_presets.py` - PRESET_NAMES, get_preset(name)

**Model Presets:**
- fast: Claude Haiku 4.5 (~$0.01/page)
- balanced: Claude Sonnet 4.5 (~$0.025/page) - DEFAULT
- thorough: Claude Opus 4.6 (~$0.15/page)
