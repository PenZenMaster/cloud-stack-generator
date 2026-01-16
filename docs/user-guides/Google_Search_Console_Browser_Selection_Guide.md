# Google Search Console Browser Selection Guide

## Overview

This guide explains how to use the browser and profile selection feature for Google Search Console OAuth authentication. This feature solves the problem where the app opens the wrong browser or profile on PCs with multiple browsers or profiles configured.

## Why This Feature Exists

When authenticating with Google Search Console, the OAuth flow opens a web browser for you to log in. By default, the system opens your default browser with your default profile. However, if you have multiple:

- **Browsers** (Chrome, Firefox, Edge, etc.)
- **Profiles** within a browser (Work profile, Personal profile, etc.)

...you may want to control which browser and profile opens for authentication. This is especially useful if your Google account is only logged in to a specific browser profile.

## Feature Capabilities

- **Auto-detect installed browsers**: Chrome, Firefox, Edge, Brave, Opera, Vivaldi, Chromium
- **Auto-detect browser profiles**: Detects all profiles configured in each browser
- **Manual browser entry**: Select a browser executable manually if auto-detection misses it
- **App-wide preference**: Your selection is saved and reused across all OAuth flows
- **Automatic fallback**: If your saved browser is uninstalled, automatically falls back to system default

## How to Use Browser Selection

### Step 1: Open GCS Verification Dialog

1. Open the application
2. Navigate to the **Google Search Console** section
3. Open the **GCS Verification Dialog**

### Step 2: Browser Selection UI

You'll see a "Browser Selection (Optional)" section with two dropdowns:

```
Browser Selection (Optional)
+------------------------------------------------------+
| Browser:  [System Default (Recommended) v] [Refresh] |
| Profile:  [Default Profile             v]            |
|                                                      |
| i Using system default browser                       |
+------------------------------------------------------+
```

**Browser Dropdown Options:**
- "System Default (Recommended)" - Uses your operating system's default browser (existing behavior)
- Detected browsers - e.g., "Google Chrome (3 profiles)", "Mozilla Firefox (2 profiles)"
- "Manual Entry..." - Opens a file dialog to select a browser executable

**Profile Dropdown Options:**
- Populated automatically when you select a browser
- Shows profile names from the browser's configuration
- Disabled when "System Default" is selected

### Step 3: Select Your Browser and Profile

1. Click the **Browser** dropdown
2. Select your desired browser (e.g., "Google Chrome (3 profiles)")
3. The **Profile** dropdown will populate with available profiles
4. Select your desired profile (e.g., "Work Profile")
5. The info label will update to show your selection

### Step 4: Authenticate

1. Click the **Authenticate** button
2. The selected browser will launch with the specified profile
3. Complete the Google OAuth login in the browser
4. The token will be saved for future use

### Step 5: Your Preference is Saved

Your browser and profile selection is automatically saved app-wide. The next time you open the GCS Verification Dialog, your saved selection will be pre-selected.

## Browser Detection Details

### Supported Browsers

| Browser | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Google Chrome | Yes | Yes | Yes |
| Mozilla Firefox | Yes | Yes | Yes |
| Microsoft Edge | Yes | Yes | Yes |
| Brave Browser | Yes | Yes | Yes |
| Opera | Yes | Yes | Yes |
| Vivaldi | Yes | Yes | Yes |
| Chromium | Yes | Yes | Yes |

### Profile Detection

**Chrome/Chromium-based browsers (Chrome, Edge, Brave, Opera, Vivaldi):**
- Reads profile metadata from `User Data/Local State` JSON file
- Detects all profiles: "Default", "Profile 1", "Profile 2", etc.
- Shows the profile display name (e.g., "Person 1", "Work")

**Firefox:**
- Reads profile metadata from `profiles.ini` INI file
- Detects all configured profiles (e.g., "default", "work")

### Detection Paths

**Windows:**
- Chrome: `%LOCALAPPDATA%\Google\Chrome\User Data`
- Firefox: `%APPDATA%\Mozilla\Firefox`
- Edge: `%LOCALAPPDATA%\Microsoft\Edge\User Data`

**macOS:**
- Chrome: `~/Library/Application Support/Google/Chrome`
- Firefox: `~/Library/Application Support/Firefox`
- Edge: `~/Library/Application Support/Microsoft Edge`

**Linux:**
- Chrome: `~/.config/google-chrome`
- Firefox: `~/.mozilla/firefox`
- Edge: `~/.config/microsoft-edge`

## Manual Browser Entry

If auto-detection doesn't find your browser:

1. Select **"Manual Entry..."** from the Browser dropdown
2. A file dialog will open
3. Navigate to your browser's executable:
   - **Windows**: Look for `.exe` files (e.g., `chrome.exe`, `firefox.exe`)
   - **macOS**: Look in `/Applications/` for `.app` bundles
   - **Linux**: Look in `/usr/bin/` for executables
4. Select the browser executable
5. Click **Open**
6. The browser will be added and selected

**Note:** Manual entry does not auto-detect profiles. You can still use the browser, but profile selection will use the browser's default profile.

## Refresh Browser List

If you install a new browser after opening the dialog:

1. Click the **Refresh** button next to the Browser dropdown
2. The browser list will be re-scanned
3. New browsers will appear in the dropdown

## Preference Storage

Your browser preference is stored in:

**Storage Location:**
- **Windows**: `C:\Users\<username>\.cloud-stack-generator\browser_prefs.json`
- **macOS**: `~/.cloud-stack-generator/browser_prefs.json`
- **Linux**: `~/.cloud-stack-generator/browser_prefs.json`

**File Format:**
```json
{
  "browser_type": "chrome",
  "browser_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "profile_name": "Work Profile",
  "profile_directory": "Profile 1"
}
```

**Security:**
- File permissions are set to owner-only (0600 on Unix-like systems)
- Contains only browser paths (not sensitive data)
- OAuth tokens are stored separately in `~/.config/cloud-stack-generator/gsc_token.json`

## Troubleshooting

### Browser Not Detected

**Problem:** Your installed browser doesn't appear in the dropdown.

**Solutions:**
1. Click the **Refresh** button to re-scan
2. Verify the browser is actually installed (check Program Files on Windows, Applications on macOS)
3. Use **"Manual Entry..."** to select the browser executable manually
4. Check that the browser is installed in a standard location (not on a network drive)

### Profile Not Detected

**Problem:** Your browser is detected but profiles are missing.

**Solutions:**
1. **Chrome/Chromium-based**: Check that `User Data/Local State` file exists and is valid JSON
2. **Firefox**: Check that `profiles.ini` file exists
3. Verify profiles are actually created in the browser (open the browser and check Settings > Profiles)
4. Use the browser without profile selection (will use default profile)

### Selected Browser Won't Launch

**Problem:** Authentication fails with "Browser launch failed" error.

**Solutions:**
1. Verify the browser executable still exists (it may have been uninstalled)
2. Close all instances of the browser and try again
3. Select **"System Default (Recommended)"** to use system default browser
4. Check that you have permission to execute the browser
5. On Windows, ensure the path doesn't contain special characters that need escaping

### Browser Opens But Wrong Profile

**Problem:** Browser launches but uses a different profile than selected.

**Causes and Solutions:**

**Chrome/Chromium:**
- Profile argument format: `--profile-directory="Profile 1"`
- Verify the profile directory name matches exactly (case-sensitive)
- Check `chrome://version/` in the browser to see the active profile path

**Firefox:**
- Profile argument format: `-P "ProfileName"`
- Verify the profile name matches exactly (case-sensitive)
- Check `about:profiles` in the browser to see available profiles

**Workaround:**
- Manually open the desired browser profile first
- Then click Authenticate (system default will use the already-open browser)

### Previously Selected Browser Uninstalled

**Problem:** You saved a browser preference but later uninstalled that browser.

**Behavior:**
- On dialog open, validation checks if the browser exists
- If not found, a warning dialog appears: "Previously selected browser not found"
- The selection automatically reverts to **"System Default (Recommended)"**
- You can select a new browser and save the preference

### Fallback Behavior

If browser launch fails for any reason, the system automatically falls back to:

1. **Custom Browser** (if selected)
2. **System Default Browser** (if custom fails)
3. **Manual URL Copy** (if all else fails - you copy/paste the OAuth URL manually)

## Technical Details

### Browser Launch Arguments

The system uses browser-specific command-line arguments to launch with profiles:

**Chromium-based (Chrome, Edge, Brave, Opera, Vivaldi):**
```bash
chrome.exe --profile-directory="Profile 1"
```

**Firefox:**
```bash
firefox.exe -P "ProfileName"
```

### OAuth Flow Process

1. User clicks **Authenticate**
2. App creates `InstalledAppFlow` with Google OAuth credentials
3. If custom browser selected:
   - App creates `CustomBrowserController` with browser path and profile args
   - Temporarily registers controller as preferred browser via `webbrowser.register()`
   - Runs `flow.run_local_server(port=0)` which opens custom browser
   - Restores original browser order after OAuth completes
4. If system default selected:
   - Runs `flow.run_local_server(port=0)` directly (existing behavior)
5. OAuth token saved to `~/.config/cloud-stack-generator/gsc_token.json`

## Best Practices

1. **Use System Default for Single Browser**: If you only have one browser or one profile, keep the default setting
2. **Save Work Profile**: If you have a dedicated work Google account in a specific profile, save that selection
3. **Test After Selection**: After selecting a browser/profile, click Authenticate to verify it works
4. **Keep Browser Updated**: Outdated browsers may have compatibility issues
5. **Don't Share Preferences**: The preference file is user-specific and shouldn't be shared

## FAQ

**Q: Can I use different browsers for different OAuth flows?**
A: No, the preference is app-wide. All OAuth flows (GCS, future integrations) will use the same browser selection.

**Q: What if I want to switch profiles temporarily?**
A: Just change the selection in the dropdown before clicking Authenticate. The new selection will be saved.

**Q: Does this work with Portable/Standalone browser installations?**
A: Yes, use "Manual Entry..." to select the portable browser's executable.

**Q: Can I disable this feature?**
A: Yes, keep "System Default (Recommended)" selected. This is the default behavior.

**Q: Does this affect existing OAuth tokens?**
A: No. Existing tokens continue to work. Browser selection only affects the authentication flow when you need to re-authenticate.

**Q: What about privacy/incognito modes?**
A: OAuth requires a profile to save login state. Incognito/private modes are not supported.

## Related Documentation

- [GCS Deployment Setup Guide](GCS_DEPLOYMENT_SETUP.md) - Setting up Google Search Console integration
- [AWS Access Key Setup Guide](AWS_Access_Key_Setup_Guide.md) - AWS credentials setup
- [Cloud Stack SOP](Cloud_Stack_SOP_S3_CloudFront.md) - Full deployment workflow

## Support

If you encounter issues not covered in this guide:

1. Check the application logs for detailed error messages
2. Verify your Google OAuth credentials are correctly configured
3. Test with system default browser first to isolate the issue
4. Report bugs with detailed steps to reproduce

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-16
**Feature Version:** Introduced in v3.6.0
