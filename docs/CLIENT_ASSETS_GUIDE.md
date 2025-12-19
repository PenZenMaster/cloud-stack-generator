# Client-Specific Assets Guide

This guide explains how to manage client-specific assets (logos, images, etc.) in the Cloud Stack Generator.

## Overview

Each client can have their own dedicated assets directory alongside their configuration files. During site generation, these assets are automatically copied to the generated site's `images/` directory.

## Directory Structure

```
config/clients/
├── {client-name}/
│   ├── assets/                  # Client-specific assets directory
│   │   ├── logo.png            # Client logo
│   │   ├── banner.jpg          # Additional images
│   │   └── favicon.ico         # Favicon
│   ├── {client}_config.yaml    # Main config
│   └── {variant}_config.yaml   # Site variant configs
```

## How It Works

1. **Storage**: Client assets are stored in `config/clients/{client-name}/assets/`
2. **Generation**: During site generation, the system:
   - First copies any global assets from `src/templates/static/images/`
   - Then copies client-specific assets (overriding global assets if names conflict)
3. **Output**: Assets end up in `output/clients/{client-name}/{site-variant}/images/`
4. **Deployment**: The `images/` directory is included in all S3 deployments

## Setting Up Client Assets

### 1. Create Assets Directory

```bash
mkdir -p config/clients/{client-name}/assets
```

### 2. Add Your Assets

Place your image files in the assets directory:

```bash
config/clients/{client-name}/assets/
├── company-logo.png
├── hero-image.jpg
└── favicon.ico
```

### 3. Reference in Config

Update your YAML config to reference the assets:

```yaml
client:
  branding:
    logo_url: images/company-logo.png  # Relative to site root
```

### 4. Generate Site

Run the generator - assets will be automatically copied:

```bash
python generate_site.py config/clients/{client-name}/{config}.yaml
```

## Supported File Types

The following image formats are automatically copied:
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- SVG (.svg)
- WebP (.webp)

## Asset Organization Options

### Option 1: Flat Structure (Recommended for Small Asset Sets)

```
assets/
├── logo.png
├── banner.jpg
└── favicon.ico
```

### Option 2: Subdirectories (For Larger Asset Sets)

```
assets/
└── images/
    ├── logo.png
    ├── products/
    │   ├── product1.jpg
    │   └── product2.jpg
    └── services/
        └── service1.jpg
```

**Note**: When using subdirectories, only files from `assets/images/` are copied. Files directly in `assets/` are also copied.

## Best Practices

1. **File Naming**: Use lowercase with hyphens (e.g., `company-logo.png`)
2. **Optimization**: Optimize images before adding them to reduce site load times
3. **Consistency**: Use consistent naming across clients (e.g., always `logo.png`)
4. **Documentation**: Add a README.md in the assets directory explaining what each file is
5. **Version Control**: Commit assets to Git for version history

## Example: Adding a Logo

1. **Download the logo** to the correct location:
   ```bash
   # Save to: config/clients/acme-corp/assets/logo.png
   ```

2. **Update the config**:
   ```yaml
   client:
     branding:
       logo_url: images/logo.png
   ```

3. **Generate and verify**:
   ```bash
   python generate_site.py config/clients/acme-corp/acme_config.yaml
   # Check: output/clients/acme-corp/{site}/images/logo.png
   ```

## Troubleshooting

### Asset Not Appearing on Site

1. Check file exists in `config/clients/{client-name}/assets/`
2. Verify file extension is supported (.png, .jpg, etc.)
3. Regenerate the site to trigger asset copying
4. Check logs for any copy errors

### Wrong Logo Appearing

- Client-specific assets override global assets
- Check both `src/templates/static/images/` and `config/clients/{client-name}/assets/`
- Client assets are copied last and will override global assets with the same name

## Migration from Global Assets

If you previously used global assets in `output/images/`:

1. Create client assets directory:
   ```bash
   mkdir -p config/clients/{client-name}/assets
   ```

2. Copy assets to new location:
   ```bash
   cp output/images/{client-logo}.png config/clients/{client-name}/assets/
   ```

3. Verify config references are correct (should be `images/{filename}.png`)

4. Regenerate sites to verify assets are copied correctly

## Related Files

- `src/core/generators/page_generator.py` - Asset copying logic in `_copy_static_assets()`
- `src/core/config/models.py` - ClientConfig.config_file_path field
- `src/core/config/parser.py` - Config loading with file path tracking
