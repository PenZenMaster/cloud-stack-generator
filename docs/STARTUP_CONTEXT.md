# AWG Startup Context

**Last Updated:** 2026-08-07
**Branch:** main
**Version:** 4.1.0
**Last Commit:** 4c8a98e - feat(seo): anchor-text rotation engine (core engine only)

---

## Last 3 Accomplishments

1. **4 critical/high SEO-risk issues closed (#33-36)** - fabricated Product ratings removed
   (f6df206); stale canonical-URL doc corrected (6883d9e); scaled template-fallback content
   gated via `ContentQualityGate` after redirecting from the issue's dead-code premise to the
   real mechanism in `seo_authority_city_page.html` (5b5ecdc); LocalBusiness+NAP schema
   restricted to `main_site` only via `resolve_entity_schema()` (6355daf).

2. **Anchor-text rotation engine core shipped (#37, 4c8a98e)** - `AnchorProfileConfig` +
   `AnchorSelector` (seeded, drift-correcting, no intra-page repeats, safety ceiling), wired
   into both page generators, all 6 hardcoded anchors replaced. Scoped to core-engine-only per
   explicit user decision - UI editor tab and `anchor_report.json` deferred, issue left OPEN
   with scope documented in a comment. Found and fixed a real blocker along the way:
   `city_page_generator.py` never set `is_backlink_site`/`main_site_url`, so the backlink CTA
   section in the live city template never rendered for any city page at all.

3. **926 -> 979 tests passing, 0 regressions** - 53 new tests across the 5 fixes; same 83
   pre-existing failures (test_backup_manager, test_template_preview, test_template_validator)
   unchanged throughout.

---

## Next 3 Priorities

1. **#38 - Content uniqueness gate** - similarity scoring and publish block across generated
   pages. Feature-sized; ask the user for scope (core logic vs full UI) before diving in.

2. **#39 - Footprint diversifier** - bucket naming, template skins, CSS prefixes, provider
   rotation. Also feature-sized.

3. **#40 - GSC indexing pipeline** - property provisioning, sitemap submit, coverage tracking.
   Also feature-sized; likely needs Google API credentials/scoping discussion.

All three came from the same 2026-08-07 risk assessment as #33-37 (see
`docs/cloud-stack-generator-assessment.md`, still untracked). #41-62 (template-system epic,
cloud-deployment backlog) are untouched and lower priority than the remaining risk-assessment
items.

---

## Current State

**Git:**
- Branch: main
- Version: 4.1.0
- Last commit: 4c8a98e (pushed as part of this checkpoint)
- Working tree: `.claude/settings.local.json` modified (local, not committed);
  `docs/cloud-stack-generator-assessment.md` and `docs/qa1.png` untracked (source assessment
  doc + screenshot, left as-is - user hasn't said whether to commit them)

**Tests:**
- Total: 979 PASSING, 83 pre-existing failures (unchanged), 6 skipped, 1 pre-existing error
- No new failures from any of #33-37
- Full-suite run time was erratic this session (118s-945s across identical runs, no code
  changes between) - system load from stacked background bash processes, not a code issue

**Blockers:**
- User still needs AWS S3/CloudFront setup for localgaragedoorcompanyreviews.com before the
  Resource Site + Providers QA from the prior session (carried over, untouched this session)

**Known Issues:**
- Camphouse Country Landscaping (SAB) GBP unresolved - try direct Place ID
- Cost display shows $0.0000 instead of actual cost - LOW priority
- Business tab "Generate with AI" buttons use OpenAI (not Claude) - works if OPENAI_API_KEY set
- `enhanced_city_page_generator.py` confirmed dead code (never instantiated anywhere) - touched
  for consistency on #36/#37 but genuine cleanup is issue #44's scope
- `google_business_profile` field in `generate_yaml_dict()` writes the raw dataclass object
  instead of a plain dict, so a full save-to-disk-and-reload round trip crashes on
  `yaml.safe_load`. Pre-existing, unrelated to this session's work
  (`test_meta_tags_feature.py::test_save_load_roundtrip_preserves_meta_tags` already covers it
  as a known failure) - worth a small fix whenever someone's in that file

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
   backlink_site, `resource_site.money_site_name`/`money_site_url` for resource sites (a
   different entity than the resource site's own editorial identity). Template usage:
   `{{ anchor(slot='footer') }}` or `{{ anchor(slot='body_contextual') }}`. `anchor_profile` on
   `CloudConfig` only gets written to YAML when the user has actually configured custom pools.

5. **When scoping a feature-sized issue** (#37 was the template) - ask the user upfront how
   much to build (core engine vs full UI vs everything across multiple commits) rather than
   assuming. Also worth checking whether the issue's named root-cause file is actually in the
   live render path before fixing it - #35 turned out to name dead code, and the real fix was
   elsewhere entirely.

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
