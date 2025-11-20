# Cloud Stack Generator - Product Roadmap

**Last Updated**: November 19, 2025
**Current Version**: 3.4.0
**Project Status**: Active Development

---

## 📋 Table of Contents

1. [Schema & Structured Data Enhancements](#1-schema--structured-data-enhancements)
2. [Multi-Cloud Deployment Support](#2-multi-cloud-deployment-support)
3. [AI Content Generation](#3-ai-content-generation)
4. [FAQ System Enhancements](#4-faq-system-enhancements)
5. [Error Logging & Monitoring](#5-error-logging--monitoring)
6. [UI & Data Model Enhancements](#6-ui--data-model-enhancements)

---

## Legend

- ✅ **Complete** - Feature implemented and tested
- 🔄 **In Progress** - Currently being developed
- 📋 **Planned** - In backlog, not yet started
- ⏸️ **Deferred** - Low priority, postponed
- ❌ **Blocked** - Waiting on dependencies

---

## 1. Schema & Structured Data Enhancements

**Priority**: HIGH
**Status**: 📋 **Planned**
**Target Version**: 3.2.0
**Estimated Effort**: 3-5 days

### 1.1 LocalBusiness Schema Enhancement

**Status**: 📋 **Planned**
**Location**: `src/core/generators/html_generator.py`

**Requirements**:
- Implement conditional LocalBusiness schema on index.html
- Only include if:
  - GBP has exposed address, OR
  - No GBP configured and published address exists

**Schema Types**:
- `Thing > Place > LocalBusiness`
- `Thing > Organization > LocalBusiness`

**Implementation Tasks**:
- [ ] Add conditional logic to schema generator
- [ ] Check GBP address exposure setting
- [ ] Check if published address exists in config
- [ ] Generate LocalBusiness schema when conditions met
- [ ] Add unit tests for conditional logic
- [ ] Update documentation

**Related Config**:
```yaml
google_business_profile:
  expose_address: true  # New field needed
contact:
  address:
    publish_on_website: true  # Existing field
```

---

### 1.2 AreaServed Property from City Pages

**Status**: 📋 **Planned**
**Location**: `src/core/generators/html_generator.py`

**Requirements**:
- Add `areaServed` property to schema
- Populate from generated city pages
- Use city names from `target_cities` configuration

**Implementation Tasks**:
- [ ] Extract city list from city_pages generator
- [ ] Build areaServed array from city names
- [ ] Add to Organization schema on index.html
- [ ] Add unit tests for areaServed generation
- [ ] Update documentation

**Example Output**:
```json
{
  "@type": "LocalBusiness",
  "areaServed": [
    {"@type": "City", "name": "Richmond, VA"},
    {"@type": "City", "name": "Norfolk, VA"},
    {"@type": "City", "name": "Virginia Beach, VA"}
  ]
}
```

---

### 1.3 Product Schema Integration

**Status**: 📋 **Planned**
**Location**: `src/core/generators/html_generator.py`

**Requirements**:
- Add `Thing > Product` schema to index.html
- Only include if business has products configured
- Link to product detail pages

**Implementation Tasks**:
- [ ] Check if products exist in config
- [ ] Generate Product schema for each product
- [ ] Add offers/pricing if available
- [ ] Link to product detail pages
- [ ] Add unit tests
- [ ] Update documentation

---

### 1.4 Service Schema Integration

**Status**: 📋 **Planned**
**Location**: `src/core/generators/html_generator.py`

**Requirements**:
- Add `Thing > Intangible > Service` schema to index.html
- Include if business offers services
- Link to service detail pages

**Implementation Tasks**:
- [ ] Check if services exist in config
- [ ] Generate Service schema for each service
- [ ] Add serviceType and category
- [ ] Link to service detail pages
- [ ] Add unit tests
- [ ] Update documentation

---

### 1.5 SameAs Property from Social Media

**Status**: 📋 **Planned**
**Location**: `src/core/generators/html_generator.py`

**Requirements**:
- Add `sameAs` property to Organization schema
- Populate from social_media URLs in config

**Implementation Tasks**:
- [ ] Extract social media URLs from config
- [ ] Build sameAs array
- [ ] Add to Organization schema
- [ ] Add unit tests
- [ ] Update documentation

**Example Output**:
```json
{
  "@type": "Organization",
  "sameAs": [
    "https://www.facebook.com/businessname",
    "https://twitter.com/businessname",
    "https://www.linkedin.com/company/businessname"
  ]
}
```

---

## 2. Multi-Cloud Deployment Support

**Priority**: MEDIUM
**Status**: 📋 **Planned**
**Target Version**: 3.3.0
**Estimated Effort**: 5-7 days

### 2.1 Google Cloud Storage Deployment

**Status**: 📋 **Planned**
**Location**: `src/core/deployment/gcs_deployer.py` (NEW)

**Requirements**:
- Deploy static websites to Google Cloud Storage
- Configure bucket for static website hosting
- Set proper permissions and CORS
- Support custom domains via Cloud CDN

**Implementation Tasks**:
- [ ] Research GCS Python SDK (google-cloud-storage)
- [ ] Create GCSDeployer class
- [ ] Implement bucket creation
- [ ] Implement website configuration
- [ ] Implement file upload with metadata
- [ ] Add authentication handling
- [ ] Create deployment UI tab
- [ ] Add unit tests
- [ ] Create deployment documentation
- [ ] Update configuration schema

**Dependencies**:
- `google-cloud-storage` Python package
- GCP service account credentials

---

### 2.2 Backblaze B2 Deployment

**Status**: 📋 **Planned**
**Location**: `src/core/deployment/b2_deployer.py` (NEW)

**Requirements**:
- Deploy static websites to Backblaze B2
- Configure bucket for website hosting
- Set proper permissions
- Support custom domains

**Implementation Tasks**:
- [ ] Research Backblaze B2 SDK
- [ ] Create B2Deployer class
- [ ] Implement bucket creation
- [ ] Implement website configuration
- [ ] Implement file upload
- [ ] Add authentication handling
- [ ] Create deployment UI tab
- [ ] Add unit tests
- [ ] Create deployment documentation
- [ ] Update configuration schema

**Dependencies**:
- `b2sdk` Python package
- Backblaze application key

---

### 2.3 Wasabi Deployment

**Status**: 📋 **Planned**
**Location**: `src/core/deployment/wasabi_deployer.py` (NEW)

**Requirements**:
- Deploy static websites to Wasabi
- S3-compatible API (can reuse S3 deployer with different endpoint)
- Configure bucket for website hosting

**Implementation Tasks**:
- [ ] Research Wasabi S3 compatibility
- [ ] Extend S3Deployer or create WasabiDeployer
- [ ] Configure Wasabi endpoint
- [ ] Test bucket creation and upload
- [ ] Add authentication handling
- [ ] Create deployment UI tab
- [ ] Add unit tests
- [ ] Create deployment documentation
- [ ] Update configuration schema

**Dependencies**:
- `boto3` (S3-compatible)
- Wasabi access keys

---

### 2.4 Multi-Cloud Deployment Manager

**Status**: 📋 **Planned**
**Location**: `src/core/deployment/deployment_manager.py` (NEW)

**Requirements**:
- Unified interface for all deployment targets
- Deploy to multiple clouds simultaneously
- Track deployment status per target
- Rollback capabilities

**Implementation Tasks**:
- [ ] Create DeploymentManager class
- [ ] Implement multi-target deployment
- [ ] Add progress tracking
- [ ] Add error handling per target
- [ ] Create deployment history tracking
- [ ] Add UI for multi-cloud selection
- [ ] Add unit tests
- [ ] Update documentation

---

## 3. AI Content Generation

**Priority**: HIGH
**Status**: 📋 **Planned**
**Target Version**: 3.4.0
**Estimated Effort**: 7-10 days

### 3.1 Business Info Content Generation

**Status**: 📋 **Planned**
**Location**: `src/core/ai/content_generator.py` (NEW)
**UI Location**: `src/ui/content_tabs/business_tab.py`

**Requirements**:
- Generate AI content for Business Info tab fields
- Support multiple AI providers (OpenAI, Anthropic, local models)
- Allow user review and editing before acceptance

**Fields to Generate**:
1. Business Description
2. Company Overview
3. Mission Statement
4. Service Guarantee
5. Service Area Description

**Implementation Tasks**:
- [ ] Research AI integration options (OpenAI API, Anthropic Claude API)
- [ ] Create AIContentGenerator base class
- [ ] Implement OpenAI provider
- [ ] Implement Anthropic provider
- [ ] Add prompt templates for each field type
- [ ] Add "Generate with AI" buttons to Business Info tab
- [ ] Create preview/accept/regenerate UI workflow
- [ ] Add API key management for AI providers
- [ ] Add unit tests
- [ ] Create user documentation
- [ ] Add cost estimation/tracking

**UI Mockup**:
```
Business Description: [existing text field]
[Generate with AI] [Preview] [Accept]
```

---

### 3.2 City Page Content Generation

**Status**: 📋 **Planned**
**Location**: `src/core/ai/city_content_generator.py` (NEW)
**UI Location**: `src/ui/content_tabs/cities_tab.py`

**Requirements**:
- Generate AI content for city page fields
- Localize content based on city context
- Support bulk generation for multiple cities

**Fields to Generate**:
1. About City
2. SEO Content Title
3. SEO Content

**Implementation Tasks**:
- [ ] Create CityContentGenerator class
- [ ] Add city-specific prompt templates
- [ ] Integrate with existing city page generator
- [ ] Add "Generate with AI" buttons to Cities tab
- [ ] Support bulk generation with progress tracking
- [ ] Add preview/accept/regenerate UI workflow
- [ ] Add unit tests
- [ ] Update documentation

---

### 3.3 Product Description Generation

**Status**: 📋 **Planned**
**Location**: `src/core/ai/product_content_generator.py` (NEW)
**UI Location**: `src/ui/content_tabs/products_tab.py`

**Requirements**:
- Generate product descriptions from basic info
- Support SEO-optimized content
- Include features and benefits

**Implementation Tasks**:
- [ ] Create ProductContentGenerator class
- [ ] Add product-specific prompt templates
- [ ] Add "Generate Description" button in Add/Edit Product dialog
- [ ] Add preview/accept/regenerate workflow
- [ ] Add unit tests
- [ ] Update documentation

---

### 3.4 FAQ Answer Generation

**Status**: 📋 **Planned**
**Location**: `src/core/ai/faq_content_generator.py` (NEW)
**UI Location**: `src/ui/content_tabs/services_tab.py`

**Requirements**:
- Generate FAQ answers from questions
- Industry-specific context
- Professional tone

**Implementation Tasks**:
- [ ] Create FAQContentGenerator class
- [ ] Add FAQ-specific prompt templates
- [ ] Add "Generate Answer" button in FAQ editor
- [ ] Add preview/accept/regenerate workflow
- [ ] Add unit tests
- [ ] Update documentation

---

### 3.5 AI Provider Management

**Status**: 📋 **Planned**
**Location**: `src/core/ai/provider_manager.py` (NEW)
**UI Location**: `src/ui/dialogs/ai_settings_dialog.py` (NEW)

**Requirements**:
- Manage multiple AI provider API keys
- Select default provider
- Track usage and costs
- Rate limiting and error handling

**Implementation Tasks**:
- [ ] Create AIProviderManager class
- [ ] Implement secure API key storage
- [ ] Create AI Settings dialog
- [ ] Add provider selection UI
- [ ] Implement usage tracking
- [ ] Add cost estimation
- [ ] Add rate limiting
- [ ] Add unit tests
- [ ] Create user documentation

---

## 4. FAQ System Enhancements

**Priority**: MEDIUM
**Status**: 🔄 **In Progress**
**Target Version**: 3.2.0
**Estimated Effort**: 2-3 days

### 4.1 Site-Wide FAQ System

**Status**: ✅ **Complete**
**Location**:
- `src/ui/content_tabs/services_tab.py`
- `src/templates/pages/faq.html`
- `src/core/generators/html_generator.py`

**Completed Features**:
- ✅ FAQ CRUD in Services Tab
- ✅ FAQ persistence to YAML
- ✅ FAQ loading from YAML
- ✅ FAQ display on faq.html page

---

### 4.2 Service-Specific FAQ System

**Status**: 📋 **Planned**
**Location**:
- `src/templates/pages/service-detail.html`
- `src/core/config/models.py`

**Requirements**:
- Associate FAQs with specific services
- Display service FAQs on service detail pages
- Separate from site-wide FAQs

**Implementation Tasks**:
- [ ] Add `faq` field to Service model
- [ ] Update services_tab.py to include service FAQs
- [ ] Update service-detail.html template to display FAQs
- [ ] Update YAML schema to support service FAQs
- [ ] Add UI for service FAQ management
- [ ] Add unit tests
- [ ] Update documentation

**Data Model**:
```python
class Service:
    name: str
    description: str
    category: str
    faq: List[FAQItem]  # NEW
```

---

### 4.3 Product-Specific FAQ System

**Status**: 📋 **Planned**
**Location**:
- `src/templates/pages/product-detail.html`
- `src/core/config/models.py`

**Requirements**:
- Associate FAQs with specific products
- Display product FAQs on product detail pages
- Separate from site-wide FAQs

**Implementation Tasks**:
- [ ] Add `faq` field to Product model
- [ ] Update products_tab.py to include product FAQs
- [ ] Update product-detail.html template to display FAQs
- [ ] Update YAML schema to support product FAQs
- [ ] Add UI for product FAQ management
- [ ] Add unit tests
- [ ] Update documentation

**Data Model**:
```python
class Product:
    name: str
    description: str
    category: str
    faq: List[FAQItem]  # NEW
```

---

## 5. Error Logging & Monitoring

**Priority**: MEDIUM
**Status**: 📋 **Planned**
**Target Version**: 3.2.0
**Estimated Effort**: 2 days

### 5.1 Application Startup Log Viewer

**Status**: 📋 **Planned**
**Location**:
- `src/ui/enhanced_main_window.py`
- `src/core/utils/log_viewer.py` (NEW)

**Requirements**:
- Tail error logs on application startup
- Display last 25 lines in a dialog or status panel
- Allow user to view full log
- Clear log option

**Implementation Tasks**:
- [ ] Create LogViewer class
- [ ] Implement log tailing (last 25 lines)
- [ ] Create startup log display dialog
- [ ] Add "View Logs" menu item
- [ ] Add "Clear Logs" option
- [ ] Add log file rotation
- [ ] Add unit tests
- [ ] Update documentation

**UI Mockup**:
```
[Startup Log Viewer]
━━━━━━━━━━━━━━━━━━━━━━━━━
2025-11-12 14:30:15 [INFO] Application started
2025-11-12 14:30:16 [INFO] Loading configuration...
2025-11-12 14:30:17 [ERROR] Failed to load template
...
[View Full Log] [Clear Log] [Close]
```

---

## 6. UI & Data Model Enhancements

**Priority**: LOW
**Status**: 📋 **Planned**
**Target Version**: TBD
**Estimated Effort**: Varies

### 6.1 New Data Fields for Schema Support

**Status**: 📋 **Planned**
**Location**: `src/core/config/models.py`

**Requirements**:
- Add new fields to support schema enhancements
- Update UI to expose new fields
- Update YAML parser

**New Fields Needed**:

```python
# GoogleBusinessProfile model
class GoogleBusinessProfile:
    expose_address: bool = True  # NEW - Control address in schema

# Social Media URLs already exist in SocialMedia model
# City pages already exist in target_cities
# Products already exist in Product model
# Services already exist in Service model
```

**Implementation Tasks**:
- [ ] Add expose_address field to GoogleBusinessProfile model
- [ ] Update GBP tab UI to include checkbox
- [ ] Update YAML parser to handle new field
- [ ] Add validation for new field
- [ ] Add unit tests
- [ ] Update documentation

---

### 6.2 Progress Bar Modal Dialog Enhancement

**Status**: 📋 **Planned**
**Priority**: MEDIUM
**Location**: All UI components with progress indicators
**Target Version**: 3.4.0
**Estimated Effort**: 2-3 days

**Current Issue**:
Progress bars are dynamically inserted into the UI layout during operations (bucket refresh, deployment, etc.), which:
- Distorts the UI layout while processes are running
- Creates visual inconsistency and layout shifts
- Does not feel like a polished application experience
- Makes the UI appear unstable

**Requirements**:
- Replace all inline progress indicators with modal dialog popups
- Modal should be non-closeable during operation
- Show "OK" or "Close" button when operation completes
- Maintain consistent visual appearance throughout operations
- Support both determinate and indeterminate progress styles

**Affected Components**:
- `src/ui/components/cloud_tab.py` - Bucket refresh progress
- `src/ui/components/cloud_tab.py` - Deployment progress
- `src/ui/components/cloud_tab.py` - Directory refresh progress
- `src/ui/components/deployment_history_tab.py` - Deployment history loading
- Any other components using `ProgressWidget` inline

**Implementation Tasks**:
- [ ] Create reusable `ProgressDialog` modal component
  - Non-modal during operation (cannot dismiss)
  - Shows progress bar (determinate or indeterminate)
  - Shows status text updates
  - Shows "OK" button when complete
  - Shows "Cancel" button for cancellable operations
- [ ] Replace `bucket_progress` inline widget with modal dialog
- [ ] Replace deployment progress inline widget with modal dialog
- [ ] Replace directory refresh progress with modal dialog
- [ ] Update all worker threads to emit signals to modal dialog
- [ ] Add success/error icons and color coding to completed modals
- [ ] Test all progress operations with new modal dialogs
- [ ] Update UI/UX documentation

**Design Specifications**:
- Modal size: 400x200px (minimum)
- Progress bar: Full width with 20px margins
- Status text: Centered, word-wrapped, 2-line minimum height
- Buttons: Right-aligned, standard platform button size
- Colors:
  - In-progress: Blue accent
  - Success: Green accent
  - Error: Red accent

**Example Usage**:
```python
# Before (inline progress):
self.bucket_progress.show_progress("Refreshing...", indeterminate=True)
# ... operation ...
self.bucket_progress.update_status("Complete")
self.bucket_progress.hide_progress()

# After (modal dialog):
self.progress_dialog = ProgressDialog(self, "Refreshing Bucket List")
self.progress_dialog.show_indeterminate()
# ... operation ...
self.progress_dialog.set_complete("Found 10 buckets", success=True)
# User clicks OK to dismiss
```

**Benefits**:
- Professional, polished UI appearance
- No layout distortion during operations
- Consistent user experience across all operations
- Clear visual feedback with completion state
- Prevents user interaction with form during operations

---

### 6.3 Persist Cloud Provider Credentials After Successful Test

**Status**: 📋 **Planned**
**Priority**: HIGH
**Location**: `src/ui/components/cloud_tab.py`, `src/core/config/models.py`
**Target Version**: 3.3.0
**Estimated Effort**: 2-3 days

**Current Issue**:
When users successfully test their cloud provider credentials (GCS, Azure, etc.), the credentials are not persisted to the client configuration. Users must re-enter credentials every time they:
- Restart the application
- Switch between clients
- Switch between cloud providers

This creates poor user experience and friction in the deployment workflow.

**Requirements**:
- Automatically save cloud provider credentials to client configuration after successful connection test
- Support multiple cloud providers (GCS, Azure Blob, Backblaze B2, Wasabi, DigitalOcean Spaces)
- Encrypt sensitive credential data (service account keys, access tokens)
- Load saved credentials when client is selected
- Allow users to update/delete saved credentials
- Maintain backwards compatibility with existing AWS profile system

**Affected Components**:
- `src/ui/components/cloud_tab.py` - Cloud Deploy tab UI
  - `test_gcs_connection()` - Save GCS credentials after successful test
  - `on_provider_changed()` - Load saved credentials when provider selected
  - `load_client_config()` - Load provider credentials when client selected
- `src/core/config/models.py` - Data models
  - Add `CloudProviderConfig` class for multi-cloud credentials
  - Add encryption/decryption methods for sensitive fields
- `src/core/config/client_config.py` - Client configuration persistence
  - Save/load cloud provider configurations
  - Encrypt/decrypt credentials before storage

**Implementation Tasks**:
- [ ] Design cloud provider credential storage schema
  - [ ] Define `CloudProviderConfig` dataclass
  - [ ] Identify sensitive fields requiring encryption
  - [ ] Design YAML structure for multi-provider configs
- [ ] Implement credential encryption/decryption
  - [ ] Use cryptography library (Fernet symmetric encryption)
  - [ ] Generate/store encryption key securely
  - [ ] Add encryption helper methods
- [ ] Update client configuration model
  - [ ] Add `cloud_providers` dict to client config
  - [ ] Add methods to save/load/delete provider configs
  - [ ] Maintain separate configs per provider type
- [ ] Update Cloud Deploy tab UI
  - [ ] Save GCS credentials after successful test
  - [ ] Save Azure credentials after successful test
  - [ ] Save other provider credentials after successful test
  - [ ] Load saved credentials on client selection
  - [ ] Load saved credentials on provider change
  - [ ] Add "Clear Saved Credentials" button per provider
- [ ] Add validation and error handling
  - [ ] Validate credentials before saving
  - [ ] Handle decryption failures gracefully
  - [ ] Warn user if credentials are outdated/invalid
- [ ] Update tests
  - [ ] Unit tests for encryption/decryption
  - [ ] Unit tests for credential save/load
  - [ ] Integration tests for full workflow
- [ ] Update documentation
  - [ ] Document credential storage format
  - [ ] Document security considerations
  - [ ] Update user guide

**Data Model Design**:
```python
@dataclass
class CloudProviderConfig:
    provider_type: str  # "google_gcs", "azure_blob", etc.
    region: str
    credentials: Dict[str, str]  # Encrypted sensitive fields
    bucket_name: Optional[str] = None
    deployment_mode: str = "storage_only"
    last_tested: Optional[datetime] = None
    is_valid: bool = False

# In ClientConfig:
@dataclass
class ClientConfig:
    # ... existing fields ...
    cloud_providers: Dict[str, CloudProviderConfig] = field(default_factory=dict)
    # Key = provider_type ("google_gcs", "azure_blob", etc.)
```

**YAML Storage Format**:
```yaml
cloud_providers:
  google_gcs:
    provider_type: google_gcs
    region: us-central1
    credentials:
      project_id: my-gcp-project  # Plain text (not sensitive)
      service_account_json_path: /path/to/key.json  # Path only
      # Encrypted fields stored in separate encrypted file or keyring
    bucket_name: my-website-bucket
    deployment_mode: storage_only
    last_tested: 2025-11-19T12:00:00
    is_valid: true

  azure_blob:
    provider_type: azure_blob
    region: eastus
    credentials:
      # Similar structure
```

**Security Considerations**:
- Use Fernet symmetric encryption for credential storage
- Store encryption key in OS keyring (keyring library)
- Never log or display decrypted credentials
- Support environment variable overrides for CI/CD
- Add option to store credentials in memory only (not persisted)

**User Workflow**:
1. User enters GCS credentials (Project ID + Service Account JSON)
2. User clicks "Test GCS Connection"
3. Connection succeeds
4. System automatically saves credentials to client config (encrypted)
5. Next time user selects this client + GCS provider:
   - Credentials are auto-populated
   - User can immediately refresh buckets or deploy
6. User can update credentials and test again
7. User can clear saved credentials via "Clear Credentials" button

**Benefits**:
- Improved user experience - no repeated credential entry
- Faster deployment workflow
- Consistent behavior across all cloud providers
- Secure credential storage with encryption
- Maintains per-client configurations
- Easy credential management and updates

---

## 📊 Implementation Priority Matrix

### Phase 1 (Version 3.2.0) - Q4 2025
**Focus**: Schema & Content Foundation
1. Schema Enhancements (1.1 - 1.5) - 3-5 days
2. Error Logging (5.1) - 2 days
3. Service/Product FAQ (4.2, 4.3) - 2-3 days

**Total Estimated Effort**: 7-10 days

---

### Phase 2 (Version 3.3.0) - Q1 2026
**Focus**: Multi-Cloud Deployment
1. Google Cloud Storage (2.1) - 2-3 days
2. Backblaze B2 (2.2) - 2-3 days
3. Wasabi (2.3) - 1-2 days
4. Deployment Manager (2.4) - 2-3 days

**Total Estimated Effort**: 7-11 days

---

### Phase 3 (Version 3.4.0) - Q2 2026
**Focus**: AI Content Generation
1. Business Content Generation (3.1) - 3-4 days
2. City Content Generation (3.2) - 2-3 days
3. Product Content Generation (3.3) - 1-2 days
4. FAQ Content Generation (3.4) - 1-2 days
5. AI Provider Management (3.5) - 2-3 days

**Total Estimated Effort**: 9-14 days

---

## 🎯 Success Metrics

### Schema Enhancements
- [ ] All schema types implemented
- [ ] Validation via Google Rich Results Test
- [ ] No schema errors in Search Console

### Multi-Cloud Deployment
- [ ] All 3 cloud providers supported
- [ ] Successful deployments to each platform
- [ ] Deployment time < 5 minutes per site

### AI Content Generation
- [ ] Content generation for all field types
- [ ] User acceptance rate > 80%
- [ ] Average generation time < 30 seconds

### FAQ System
- [ ] FAQs supported on all page types
- [ ] CRUD operations functional
- [ ] Proper schema markup on all FAQ displays

### Error Logging
- [ ] All errors captured in logs
- [ ] Startup log viewer implemented
- [ ] Log rotation working

---

## 📝 Notes

**QA Feedback Source**: All items derived from `qa_artifacts/mods.txt`
**Last Review**: November 12, 2025
**Next Review**: After Phase 1 completion

**Related Documentation**:
- [Project Status](projectStatus.md)
- [AWG Project Plan](AWG-Project-Plan.md)
- [Backlink Site Strategy](BACKLINK_SITE_STRATEGY.md)
- [AWS S3 Deployment Setup](AWS_S3_DEPLOYMENT_SETUP.md)

---

## 🔄 Changelog

### November 19, 2025
- Added section 6.2: Progress Bar Modal Dialog Enhancement
- Added section 6.3: Persist Cloud Provider Credentials After Successful Test
- Updated current version to 3.2.0
- Added UI/UX improvement task for modal progress dialogs
- Added credential persistence enhancement for multi-cloud support
- Fixed: Changed "S3 Bucket Configuration" label to "Cloud Storage Bucket Configuration"

### November 12, 2025
- Initial roadmap created from qa_artifacts/mods.txt
- All items categorized and prioritized
- Implementation tasks defined
- Phase timeline estimates added
