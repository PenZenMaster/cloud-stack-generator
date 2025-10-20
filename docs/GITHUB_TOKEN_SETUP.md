# GitHub Token Security Guide

## 🔐 Secure Token Storage Options

Your GitHub Personal Access Token has been set up with multiple secure storage options:

### Option 1: Environment File (.env) - ✅ CURRENT SETUP
```
Location: E:\projects\cloud-stack-generator\.env
Security: ✅ Excluded from Git via .gitignore
Usage: Development and testing
```

**How to add your token:**
1. Open the `.env` file in your project root
2. Replace `your_token_here` with your actual token:
   ```
   GITHUB_TOKEN=ghp_your_actual_token_here
   ```
3. Save the file

### Option 2: Windows Credential Manager (Most Secure)
```
Location: Windows Credential Manager
Security: ✅ Encrypted by Windows
Usage: Production and daily use
```

**How to set up:**
1. Run: `python tools\github_token_manager.py`
2. Choose option 2 when prompted
3. Your token will be stored securely in Windows

### Option 3: Environment Variable (CI/CD)
```
Location: System/User environment variables
Security: ✅ Not stored in files
Usage: Continuous integration
```

**How to set up:**
```cmd
# Command Prompt
set GITHUB_TOKEN=your_token_here

# PowerShell
$env:GITHUB_TOKEN='your_token_here'

# Permanent (System Properties)
setx GITHUB_TOKEN "your_token_here"
```

## 🚀 Quick Setup

### Method 1: Manual Edit (Fastest)
1. Open `E:\projects\cloud-stack-generator\.env`
2. Replace the placeholder:
   ```
   GITHUB_TOKEN=ghp_your_actual_token_here
   ```
3. Save and close

### Method 2: Interactive Setup
1. Double-click `setup_github_token.bat`
2. Follow the prompts
3. Choose your preferred storage method

### Method 3: Command Line
```cmd
cd E:\projects\cloud-stack-generator
python tools\github_token_manager.py
```

## 🔍 Token Validation

The system will automatically:
- ✅ Validate your token works with GitHub API
- ✅ Show your GitHub username if valid
- ❌ Alert you if the token is invalid

## 🛡️ Security Best Practices

### ✅ DO:
- Store token in `.env` file for development
- Use Windows Credential Manager for production
- Set token expiration (recommend 90 days)
- Rotate tokens regularly

### ❌ DON'T:
- Commit `.env` file to Git (already protected)
- Share your token with others
- Use tokens in public repositories
- Set overly broad permissions

## 🔧 Required Token Permissions

When creating your GitHub token, select these scopes:
```
✅ repo - Full control of private repositories
✅ public_repo - Access public repositories  
✅ write:discussion - Write access to discussions
✅ project - Full control of projects
```

## 🚨 If Your Token is Compromised

1. **Immediately revoke** the token on GitHub:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Find your token and click "Delete"

2. **Generate a new token** with the same permissions

3. **Update your local storage**:
   - Edit `.env` file with new token, OR
   - Run `python tools\github_token_manager.py` again

## 📞 Need Help?

If you encounter issues:
1. Check that Python is installed and in your PATH
2. Verify your GitHub token has the correct permissions
3. Ensure the token isn't expired
4. Run the validation: `python tools\github_token_manager.py`

## ✅ Verification

To verify your setup is working:
```cmd
cd E:\projects\cloud-stack-generator
python -c "from tools.github_token_manager import GitHubTokenManager; mgr = GitHubTokenManager(); token = mgr.get_token(); print('✅ Token found' if token else '❌ No token found')"
```

Your token is now securely configured and ready for GitHub API access! 🎉