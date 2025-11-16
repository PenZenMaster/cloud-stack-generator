# Mode B Implementation Plan - Phase 2

**Version**: 3.2.0
**Date**: November 16, 2025
**Priority**: HIGH - User cannot use AWS Console workflow

---

## Executive Summary

Shift from current hybrid Mode A approach to full two-mode architecture:
- **Mode A**: S3-only deployment (no CloudFront, public access)
- **Mode B**: Full CDN deployment with auto-created CloudFront + OAC

**Critical Requirement**: User must NEVER need to access AWS Console. All CloudFront distributions must be auto-created/retrieved by the app.

---

## Architecture Changes

### Current State (v3.1.0)
```
Mode A: S3 deployment + optional manual CloudFront
Mode B: Disabled (Coming in Phase 2)

YAML Config:
  - Single deployment configuration
  - Meta tags global to config
  - Manual CloudFront distribution ID entry
```

### Target State (v3.2.0)
```
Mode A: S3-only deployment (no CloudFront)
  - Direct S3 website hosting
  - Public bucket access
  - CloudFront section grayed out
  - SEO meta tags embedded in HTML

Mode B: CloudFront + OAC (auto-managed)
  - Auto-create CloudFront distribution if needed
  - Retrieve existing distribution if already created
  - Origin Access Control (private bucket)
  - Always invalidate cache on deploy
  - SEO meta tags embedded in HTML

Multi-Deployment Support:
  - Track multiple bucket/directory pairs
  - Store meta tags per deployment
  - Deployment history in YAML
  - Example:
    * portable-sanitation-solutions/clean-restroom-rentals-va
    * portable-sanitation-solutions/clean-restroom-rentals-fl
    * different-bucket/client-name
```

---

## Detailed Requirements

### 1. Mode A: S3-Only Deployment

**UI Changes:**
- Gray out entire "CloudFront Distribution (Optional)" section when Mode A selected
- Remove Distribution ID input field interaction
- Remove auto-invalidate checkbox interaction
- Clear visual indication that CloudFront is not used

**Functionality:**
- Deploy to S3 with public-read ACLs
- Enable static website hosting on bucket
- Return S3 website URL: `https://bucket.s3-website-region.amazonaws.com/directory/`
- **SEO Meta Tags**: Must still embed correctly in generated HTML
- No CloudFront operations

**Code Changes:**
```python
# cloud_tab.py
def on_deployment_mode_changed(self):
    if self.s3_mode_radio.isChecked():
        # Gray out CloudFront section
        self.cloudfront_settings_group.setEnabled(False)
        self.cloudfront_settings_group.setStyleSheet("color: #999;")
    else:
        # Enable CloudFront section for Mode B
        self.cloudfront_settings_group.setEnabled(True)
        self.cloudfront_settings_group.setStyleSheet("")
```

### 2. Mode B: CloudFront + OAC (Auto-Managed)

**CloudFront Auto-Creation:**
```python
def get_or_create_cloudfront_distribution(
    bucket_name: str,
    directory: str,
    region: str
) -> str:
    """
    Get existing CloudFront distribution or create new one.

    Strategy:
    1. Check if distribution already exists for this bucket/directory
       - Search by origin domain + origin path
    2. If exists: return distribution ID
    3. If not: create new distribution with OAC

    Returns:
        distribution_id (str): E.g., E1DKVV3777HLXC
    """
    pass
```

**Distribution Configuration:**
- **Origin**: `bucket-name.s3.region.amazonaws.com`
- **Origin Path**: `/directory` (e.g., `/clean-restroom-rentals-va`)
- **Origin Access Control**: Create OAC identity
- **S3 Bucket Policy**: Update to allow CloudFront OAC access only
- **Bucket Public Access**: BLOCK (private bucket)
- **Default Root Object**: `index.html`
- **Cache Behavior**: Default settings
- **Comment**: `Auto-created for {business_name} - {directory}`

**Always Invalidate Cache:**
- Every deployment to Mode B auto-invalidates: `/*`
- No checkbox needed (always on)
- Show invalidation ID in deployment output

**Code Changes:**
```python
# s3_manager.py
def create_cloudfront_distribution_with_oac(
    self,
    bucket_name: str,
    directory: str,
    region: str,
    comment: str
) -> Tuple[bool, str, str]:
    """
    Create CloudFront distribution with Origin Access Control.

    Returns:
        (success, distribution_id, domain_name)
    """
    # 1. Create OAC
    # 2. Create distribution with OAC
    # 3. Update S3 bucket policy to allow OAC
    # 4. Block public access on bucket
    # 5. Return distribution ID and domain
    pass

def find_distribution_by_origin(
    self,
    bucket_name: str,
    directory: str
) -> Optional[str]:
    """Find existing distribution for bucket/directory"""
    # List all distributions
    # Match by origin domain + origin path
    # Return distribution ID if found
    pass
```

### 3. Multi-Deployment Architecture

**YAML Configuration Structure:**

```yaml
# config/clients/clean_restroom_rental_va.yaml

client:
  business_name: "Clean Restroom Rentals Virginia"
  domain: "cleanrestroomrentalsva.com"

# NEW: Deployments section - tracks all deployments for this client
deployments:
  - deployment_id: "portable-sanitation-solutions-clean-restroom-rentals-va"
    bucket: "portable-sanitation-solutions"
    directory: "clean-restroom-rentals-va"
    region: "us-east-1"
    mode: "cloudfront"  # or "s3"
    cloudfront_distribution_id: "E1DKVV3777HLXC"
    cloudfront_domain: "d35dpqbrqrzecj.cloudfront.net"
    last_deployed: "2025-11-16T10:00:00Z"

    # Meta tags specific to this deployment
    meta_tags:
      - name: "google-site-verification"
        content: "abc123xyz"
      - property: "og:title"
        content: "Porta Potty Rentals VA"
      - property: "og:description"
        content: "Clean portable restroom rentals in Virginia"

  - deployment_id: "portable-sanitation-solutions-clean-restroom-rentals-fl"
    bucket: "portable-sanitation-solutions"
    directory: "clean-restroom-rentals-fl"
    region: "us-east-1"
    mode: "cloudfront"
    cloudfront_distribution_id: "E2ABC123XYZ456"
    cloudfront_domain: "d123abc456xyz.cloudfront.net"
    last_deployed: "2025-11-14T15:30:00Z"

    # Different meta tags for FL deployment
    meta_tags:
      - name: "google-site-verification"
        content: "fl456def"
      - property: "og:title"
        content: "Porta Potty Rentals FL"
      - property: "og:description"
        content: "Clean portable restroom rentals in Florida"

# Services and cities remain the same
services: [...]
service_areas: [...]
```

**UI Changes:**

**Deployment History Panel:**
```
╔═══════════════════════════════════════════════════════════╗
║ Deployment History                                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║ ┌─────────────────────────────────────────────────────┐ ║
║ │ portable-sanitation-solutions/clean-restroom-...va │ ║
║ │ Mode: CloudFront | Last: 2025-11-16 10:00 AM       │ ║
║ │ Distribution: E1DKVV3777HLXC                        │ ║
║ │ URL: https://d35dpqbrqrzecj.cloudfront.net/        │ ║
║ │                                                     │ ║
║ │ [Re-Deploy] [Update Meta Tags] [Delete]            │ ║
║ └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║ ┌─────────────────────────────────────────────────────┐ ║
║ │ portable-sanitation-solutions/clean-restroom-...fl │ ║
║ │ Mode: CloudFront | Last: 2025-11-14 3:30 PM        │ ║
║ │ Distribution: E2ABC123XYZ456                        │ ║
║ │ URL: https://d123abc456xyz.cloudfront.net/         │ ║
║ │                                                     │ ║
║ │ [Re-Deploy] [Update Meta Tags] [Delete]            │ ║
║ └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║                         [+ New Deployment]                ║
╚═══════════════════════════════════════════════════════════╝
```

**Code Changes:**
```python
# models.py
@dataclass
class DeploymentConfig:
    """Individual deployment configuration"""
    deployment_id: str
    bucket: str
    directory: str
    region: str
    mode: str  # "s3" or "cloudfront"
    cloudfront_distribution_id: Optional[str] = None
    cloudfront_domain: Optional[str] = None
    last_deployed: Optional[str] = None
    meta_tags: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class ClientConfig:
    """Existing client config + deployments"""
    # ... existing fields ...
    deployments: List[DeploymentConfig] = field(default_factory=list)
```

### 4. Semantic Versioning

**Version Update**: `3.1.0` → `3.2.0`

Justification:
- Minor version bump (new features, backward compatible)
- New feature: Mode B with CloudFront auto-creation
- New feature: Multi-deployment support
- New feature: Per-deployment meta tags

**Update Locations:**
1. `src/__init__.py` or version file
2. Help → About dialog
3. README.md
4. CHANGELOG.md

**About Dialog:**
```
Cloud Stack Generator
Version 3.2.0

New in v3.2.0:
- Mode B: CloudFront + OAC auto-deployment
- Multi-deployment support (same config, multiple destinations)
- Per-deployment meta tags
- CloudFront distribution auto-creation
- No AWS Console required

Copyright 2025 Rank Rocket Co
```

---

## Implementation Phases

### Phase 1: Mode A Cleanup (2 hours)
1. Gray out CloudFront section when Mode A selected
2. Remove CloudFront operations from Mode A deploy
3. Verify SEO meta tags still work
4. Update tests

### Phase 2: Multi-Deployment Foundation (4 hours)
1. Extend YAML schema with deployments array
2. Create DeploymentConfig dataclass
3. Update parser to handle new structure
4. Maintain backward compatibility with old configs
5. Add deployment history UI panel

### Phase 3: CloudFront Auto-Creation (6 hours)
1. Implement `create_cloudfront_distribution_with_oac()`
2. Implement `find_distribution_by_origin()`
3. Implement OAC identity creation
4. Update S3 bucket policy for OAC
5. Add distribution creation progress indicator
6. Handle distribution creation failures

### Phase 4: Mode B Implementation (4 hours)
1. Enable Mode B radio button
2. Wire up Mode B deployment handler
3. Auto-create/retrieve CloudFront distribution
4. Deploy with OAC (private bucket)
5. Always invalidate cache
6. Return CloudFront URL

### Phase 5: Per-Deployment Meta Tags (3 hours)
1. Store meta tags per deployment in YAML
2. Load correct meta tags for selected deployment
3. Update HTML generator to use deployment meta tags
4. Test meta tag isolation

### Phase 6: Versioning & Polish (2 hours)
1. Update version to 3.2.0
2. Update About dialog
3. Update README and CHANGELOG
4. Run full test suite
5. Update documentation

**Total Estimated Time**: 21 hours (~3 days)

---

## Testing Strategy

### Unit Tests
- [ ] Mode A grays out CloudFront section
- [ ] Mode B creates CloudFront distribution
- [ ] Find existing distribution by origin
- [ ] Create OAC identity
- [ ] Update S3 bucket policy
- [ ] Parse deployments array from YAML
- [ ] Store per-deployment meta tags
- [ ] Load correct meta tags for deployment

### Integration Tests
- [ ] Full Mode A deploy (S3-only)
- [ ] Full Mode B deploy (new CloudFront creation)
- [ ] Full Mode B deploy (existing CloudFront reuse)
- [ ] Multi-deployment to same bucket
- [ ] Meta tags isolated per deployment

### Manual QA
- [ ] Deploy to new directory (auto-create CloudFront)
- [ ] Deploy to existing directory (reuse CloudFront)
- [ ] Verify CloudFront URL works
- [ ] Verify different meta tags per deployment
- [ ] Test Mode A (S3-only, no CloudFront)

---

## Risk Assessment

### High Risk
- **CloudFront creation can fail**: Add retry logic + clear error messages
- **S3 bucket policy updates**: Careful not to break existing access
- **Backward compatibility**: Old YAML configs must still work

### Medium Risk
- **OAC permissions**: May need IAM policy updates for CloudFront OAC
- **Multi-deployment UI complexity**: Keep it simple and intuitive

### Low Risk
- **Version update**: Straightforward
- **Mode A graying out**: Simple UI change

---

## Backward Compatibility

**Old YAML configs (v3.1.0):**
```yaml
client:
  business_name: "..."
  cloudfront_distribution_id: "E1DKVV3777HLXC"  # OLD field
meta_tags: [...]  # Global meta tags
```

**Migration Strategy:**
```python
def migrate_config_to_v3_2(config: dict) -> dict:
    """Migrate old config to new deployments structure"""
    if 'deployments' not in config:
        # Create single deployment from old structure
        deployment = {
            'deployment_id': f"{config['bucket']}-{config['directory']}",
            'bucket': config.get('bucket', ''),
            'directory': config.get('directory', ''),
            'mode': 'cloudfront' if config.get('cloudfront_distribution_id') else 's3',
            'cloudfront_distribution_id': config.get('cloudfront_distribution_id'),
            'meta_tags': config.get('meta_tags', [])
        }
        config['deployments'] = [deployment]

        # Remove old fields
        config.pop('cloudfront_distribution_id', None)

    return config
```

---

## User Workflow Examples

### Example 1: First Deployment (Mode B)
1. User creates config: `clean_restroom_rental_va.yaml`
2. Sets bucket: `portable-sanitation-solutions`
3. Sets directory: `clean-restroom-rentals-va`
4. Selects **Mode B: CloudFront + OAC**
5. Clicks Deploy
6. **App auto-creates CloudFront distribution** (no AWS Console!)
7. App shows progress: "Creating CloudFront distribution..."
8. App deploys to S3 with private access
9. App updates bucket policy for OAC
10. App invalidates CloudFront cache
11. App saves distribution ID to YAML
12. **Result**: CloudFront URL ready to use

### Example 2: Second Deployment (Same Config, Different Directory)
1. User clicks "+ New Deployment" in deployment history
2. Sets bucket: `portable-sanitation-solutions`
3. Sets directory: `clean-restroom-rentals-fl`
4. Changes meta tags (different Google verification for FL)
5. Selects **Mode B: CloudFront + OAC**
6. Clicks Deploy
7. **App auto-creates NEW CloudFront distribution** for FL
8. App saves as second deployment in YAML
9. **Result**: Two deployments, two CloudFront distributions, different meta tags

### Example 3: Re-Deploy Existing (Update Content)
1. User selects deployment from history
2. Clicks "Re-Deploy"
3. App uses existing CloudFront distribution
4. App invalidates cache
5. **Result**: Content updated, same CloudFront URL

---

## Next Steps

**Immediate Actions:**
1. ✅ Review this plan
2. ✅ Approve implementation approach
3. ⏳ Start Phase 1: Mode A cleanup
4. ⏳ Implement multi-deployment YAML structure
5. ⏳ Implement CloudFront auto-creation

**Questions for User:**
1. Should we keep old configs working (backward compatibility)?
2. When Mode B creates CloudFront, should we show detailed progress?
3. Should deployment history be in a separate tab or section?
4. Any specific OAC permissions or IAM role requirements?

---

## Success Criteria

- [  ] User can deploy Mode A (S3-only) without touching CloudFront
- [ ] User can deploy Mode B (CloudFront + OAC) without AWS Console
- [ ] CloudFront distributions auto-created with correct origin path
- [ ] Multiple deployments to same bucket with different directories work
- [ ] Each deployment has isolated meta tags
- [ ] Deployment history tracks all deployments
- [ ] Version updated to 3.2.0
- [ ] All tests passing
- [ ] Documentation updated
