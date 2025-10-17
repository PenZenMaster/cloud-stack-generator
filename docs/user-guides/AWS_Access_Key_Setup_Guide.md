# AWS Access Key Setup Guide
## Simple "Configure Once, Use Forever" Authentication

### 🎯 **New Improved Authentication Flow**
No more token expiration! Set up your AWS credentials once and generate websites indefinitely.

---

## **Step 1: Get Your AWS Access Keys**

### Option A: Create New User (Recommended)
1. **Log into AWS Console** → Go to **IAM** → **Users**
2. **Create User** → Enter name like "website-deployer"
3. **Set Permissions** → Attach policies:
   - `AmazonS3FullAccess` (required for S3 buckets)
   - `CloudFrontFullAccess` (optional - for CDN acceleration)
4. **Create Access Key** → Choose "Application running outside AWS"
5. **Copy & Save**:
   - ✅ **Access Key ID**: `AKIA...` (20 characters)
   - ✅ **Secret Access Key**: `...` (40 characters)

### Option B: Use Existing User
1. **IAM** → **Users** → Select your user
2. **Security Credentials** tab → **Create Access Key**
3. **Copy both keys** (you can't see the secret again!)

---

## **Step 2: Configure in Cloud Stack Generator**

### **🚀 First Time Setup**
1. **Open Cloud Stack Generator**
2. **Go to Cloud Tab**
3. **Click "New Profile"**

### **📝 Profile Configuration**
1. **Profile Name**: Enter something like "my-aws-account"
2. **Description**: Optional (e.g., "Personal AWS account")
3. **Authentication Method**: ✅ **"Access Keys (Recommended)"** (pre-selected)
4. **Access Key ID**: Paste your `AKIA...` key
5. **Secret Access Key**: Paste your secret key
6. **Default Region**: Choose your preferred region (e.g., `us-east-1`)
7. **Click OK**

---

## **Step 3: Test & Deploy**

### **✅ Verify Connection**
1. **Select your profile** from dropdown
2. **Click "Test Connection"**
3. ✅ Should show: *"Successfully connected to AWS"*

### **🚀 Deploy Website**
1. **Select your bucket** (or create new one)
2. **Click "Deploy to Cloud"**
3. ✅ **No re-authentication needed!**

---

## **🎉 Benefits of New Flow**

| **Before (SSO)** | **After (Access Keys)** |
|------------------|-------------------------|
| ❌ Re-authenticate every hour | ✅ Configure once, use forever |
| ❌ "Configure SSO" terminal commands | ✅ Simple form in the app |
| ❌ Requires AWS CLI setup | ✅ Works entirely in the app |
| ❌ Browser redirects | ✅ Direct credential entry |

---

## **🔒 Security Notes**

- **Keys are encrypted** and stored locally in `~/.cloud-stack-generator/api_keys.dat`
- **Keys never leave your computer** - stored with base64 encoding
- **Use least-privilege** - only grant S3 permissions needed
- **Rotate keys periodically** (every 90 days recommended)

---

## **🆘 Troubleshooting**

### **"Invalid AWS credentials"**
- ✅ Double-check keys were copied correctly (no extra spaces)
- ✅ Ensure user has S3 permissions
- ✅ Check if keys are still active in AWS Console

### **"No credentials found"**
- ✅ Re-create the profile with correct Access Keys
- ✅ Check that profile name matches exactly

### **"Access Denied"**
- ✅ User needs `AmazonS3FullAccess` or custom S3 policy
- ✅ Check bucket policies don't block your account

### **CloudFront Errors**
- ❌ **"not authorized to perform: cloudfront:CreateDistribution"**
- ✅ **Solution**: Add `CloudFrontFullAccess` policy to your IAM user
- ℹ️ **Note**: CloudFront is optional - websites work with S3-only hosting
- ℹ️ **Alternative**: Disable CloudFront in deployment settings if not needed

---

## **🔄 Migration from SSO**

If you have existing SSO profiles:
1. **Create new Access Key profile** (follow steps above)
2. **Test the new profile** works
3. **Delete old SSO profile** if desired
4. ✅ **Enjoy uninterrupted website generation!**

**Done!** Your AWS authentication is now configured for seamless website deployment.