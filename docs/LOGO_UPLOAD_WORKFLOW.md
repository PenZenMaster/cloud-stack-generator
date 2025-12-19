# Logo & Hero Background Upload Workflow

## Overview

The logo and hero background upload system now uses the client-specific assets approach, automatically organizing and managing image assets for each client.

## How It Works

### Step 1: Upload in Branding Tab

**Logo Upload:**
1. Navigate to the **Branding & Style** tab
2. Find the "Logo & Branding Assets" section
3. Click **"Upload Logo"** button
4. Select your logo file (PNG, JPG, JPEG, SVG, GIF, BMP supported)
5. The file path is stored temporarily

**Hero Background Upload:**
1. In the same "Logo & Branding Assets" section
2. Click **"Upload Image"** button (for Hero Background)
3. Select your hero background image (PNG, JPG, JPEG, WebP, GIF, BMP supported)
4. The file path is stored temporarily

### Step 2: Save Configuration

When you save the configuration (**File → Save** or **Ctrl+S**):

1. **Automatic Asset Copying**:
   - The system creates `config/clients/{client-name}/assets/` directory
   - Logo file is copied to the assets directory
   - Hero background file is copied to the assets directory

2. **Path Conversion**:
   - Original path: `C:\Users\...\my-logo.png`
   - Saved in config: `images/my-logo.png` (relative path)

3. **Confirmation**:
   - Status bar shows: "Copied logo to client assets: my-logo.png"
   - Or: "Copied hero background to client assets: hero-bg.jpg"

### Step 3: Site Generation

When you generate the website:

1. The `page_generator.py` automatically copies assets from `config/clients/{client-name}/assets/` to the output directory
2. Assets end up in: `output/clients/{client-name}/{site-variant}/images/`
3. The website references them as: `images/logo.png` (works correctly)

## Directory Structure

```
config/clients/
└── {client-name}/
    ├── assets/                          # Client-specific assets
    │   ├── my-company-logo.png          # Logo uploaded via UI
    │   ├── hero-background.jpg          # Hero bg uploaded via UI
    │   └── other-assets.png             # Additional assets
    ├── {client}_config.yaml             # Config file with relative paths

↓ After Generation ↓

output/clients/{client-name}/{site-variant}/
└── images/
    ├── my-company-logo.png              # Automatically copied
    ├── hero-background.jpg              # Automatically copied
    └── other-assets.png                 # Automatically copied
```

## Config File Format

When saved, the YAML config contains relative paths:

```yaml
client:
  branding:
    logo:
      logo_url: images/my-company-logo.png
      hero_background_image_url: images/hero-background.jpg
```

## URL Support

You can also enter URLs directly instead of uploading files:

1. **Public CDN URLs**: `https://cdn.example.com/logo.png`
   - Not copied to assets directory
   - Used directly in generated sites

2. **Local File Paths**: `C:\Users\...\logo.png`
   - Automatically copied to assets on save
   - Converted to relative path

The system automatically detects whether the path is a local file (exists on disk) or a URL.

## Benefits

1. **Organized**: Each client's assets stay with their configuration
2. **Portable**: Move the config directory and assets move too
3. **Version Control**: Assets can be committed to Git alongside configs
4. **Automatic**: No manual file copying required
5. **Isolated**: Client A's logo doesn't interfere with Client B's

## Common Workflows

### New Client Setup

1. Create new configuration in UI
2. Fill in business details (gives client a name)
3. Go to Branding & Style tab
4. Upload logo and hero background
5. Save configuration
   - Assets automatically copied to: `config/clients/{sanitized-business-name}/assets/`
6. Generate site
   - Assets automatically included in output

### Updating Logo

1. Open existing configuration
2. Go to Branding & Style tab
3. Click "Upload Logo" and select new file
4. Save configuration
   - Old logo is replaced in `config/clients/{client-name}/assets/`
   - Config updated with new filename

### Multiple Site Variants

If one client has multiple site variants (e.g., main site, backlink sites):

1. All variants reference the same `assets/` directory
2. Logo is shared across all site variants
3. Each generated site gets its own copy in its output directory

## Troubleshooting

### Logo Not Appearing After Upload

**Check:**
1. Did you save the configuration after uploading?
2. Check `config/clients/{client-name}/assets/` - is the logo there?
3. Regenerate the site to trigger asset copying

### Wrong Logo Appearing

**Issue**: Old logo showing instead of new one

**Solution**:
1. Check the filename in `config/clients/{client-name}/assets/`
2. If you uploaded a file with the same name, clear browser cache
3. Or rename the new logo before uploading

### Asset Copy Failed

**Error Message**: "Could not copy logo file"

**Common Causes**:
1. Original file was moved or deleted
2. No write permission to config directory
3. Disk full

**Solution**:
1. Ensure original file still exists
2. Check directory permissions
3. Free up disk space

## Manual Asset Management

You can also manually add assets:

1. Create/navigate to: `config/clients/{client-name}/assets/`
2. Copy image files directly there
3. Edit the YAML config to reference them:
   ```yaml
   logo_url: images/your-logo.png
   ```
4. Regenerate the site

This is useful for:
- Batch operations
- Automated scripts
- Working with version control

## Related Documentation

- `docs/CLIENT_ASSETS_GUIDE.md` - Complete asset system documentation
- `config/clients/unites-structural-systems/assets/README.md` - Example assets directory
- `LOGO_DOWNLOAD_INSTRUCTIONS.txt` - Instructions for United Structural Systems logo
