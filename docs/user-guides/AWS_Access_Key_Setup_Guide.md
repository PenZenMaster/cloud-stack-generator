# AWS Access Key Setup Guide
## Simple "Configure Once, Use Forever" Authentication

### 🎯 **New Improved Authentication Flow**
No more token expiration! Set up your AWS credentials once and generate websites indefinitely.

---

## **Step 1: Create New IAM User (Recommended for Security)**

### **Why Create a Dedicated User?**
- ✅ **Least Privilege**: Grant only necessary permissions
- ✅ **Auditability**: Track exactly what this application does
- ✅ **Security**: Isolate access - if compromised, only this user is affected
- ✅ **Key Rotation**: Easy to rotate credentials without affecting other services

### **Detailed IAM User Creation Steps**

1. **Log into AWS Console**
   - Go to https://console.aws.amazon.com/
   - Navigate to **IAM** service (search "IAM" in top search bar)
   - Click **Users** in left sidebar
   - Click **Create user** button (top right)

2. **User Details**
   - **User name**: `cloud-stack-generator-deployer` (or similar descriptive name)
   - **Provide user access to the AWS Management Console**: ❌ **Leave UNCHECKED** (not needed)
   - Click **Next**

3. **Set Permissions** - Choose Option 1 (Recommended) or Option 2:

   #### **Option 1: Least-Privilege Custom Policy (RECOMMENDED)**
   - Select **Attach policies directly**
   - Click **Create policy** button (opens new tab)
   - Click **JSON** tab
   - Replace content with the policy below
   - Click **Next**
   - **Policy name**: `CloudStackGeneratorAccess`
   - **Description**: `Minimal permissions for Cloud Stack Generator S3 deployment`
   - Click **Create policy**
   - Return to previous tab, click refresh icon, search for `CloudStackGeneratorAccess`
   - ✅ Check the box next to your new policy
   - Click **Next**

   **Least-Privilege Policy JSON:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "S3BucketManagement",
         "Effect": "Allow",
         "Action": [
           "s3:CreateBucket",
           "s3:DeleteBucket",
           "s3:ListBucket",
           "s3:GetBucketWebsite",
           "s3:PutBucketWebsite",
           "s3:DeleteBucketWebsite",
           "s3:GetBucketPolicy",
           "s3:PutBucketPolicy",
           "s3:DeleteBucketPolicy",
           "s3:PutBucketPublicAccessBlock",
           "s3:GetBucketPublicAccessBlock",
           "s3:PutBucketAcl",
           "s3:GetBucketAcl",
           "s3:GetBucketLocation",
           "s3:ListAllMyBuckets"
         ],
         "Resource": [
           "arn:aws:s3:::*"
         ]
       },
       {
         "Sid": "S3ObjectManagement",
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "s3:DeleteObject",
           "s3:PutObjectAcl",
           "s3:GetObjectAcl"
         ],
         "Resource": [
           "arn:aws:s3:::*/*"
         ]
       }
     ]
   }
   ```

   #### **Option 2: AWS Managed Policies (Quick Setup)**
   - Select **Attach policies directly**
   - Search and select: ✅ `AmazonS3FullAccess`
   - (Optional) Search and select: ✅ `CloudFrontFullAccess` (for HTTPS/CDN)
   - Click **Next**

   **Note**: AWS managed policies are broader than needed but simpler to set up.

4. **Review and Create**
   - Review user details and permissions
   - (Optional) Add tags:
     - Key: `Project`, Value: `CloudStackGenerator`
     - Key: `Purpose`, Value: `WebsiteDeployment`
   - Click **Create user**

5. **Create Access Key**
   - After user creation, click on the user name
   - Click **Security credentials** tab
   - Scroll to **Access keys** section
   - Click **Create access key**
   - Choose use case: **Application running outside AWS** or **Command Line Interface (CLI)**
   - Click **Next**
   - (Optional) Description: `Cloud Stack Generator Desktop App`
   - Click **Create access key**

6. **Save Your Credentials** ⚠️ **CRITICAL**
   - ✅ **Access Key ID**: `AKIA...` (20 characters) - Copy and save
   - ✅ **Secret Access Key**: `...` (40 characters) - Copy and save
   - **Download .csv file** (backup - store securely)
   - ⚠️ **You cannot view the secret key again after closing this dialog!**
   - Click **Done**

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

## **🔒 Security Best Practices**

### **Credential Storage**
- ✅ **Keys are encrypted** and stored locally in `~/.cloud-stack-generator/api_keys.dat`
- ✅ **Keys never leave your computer** - no cloud synchronization
- ✅ **Base64 encoding** protects against casual inspection
- ⚠️ **Never commit** credentials to git repositories
- ⚠️ **Never share** your Secret Access Key

### **Access Key Rotation Schedule**
Rotate your access keys regularly to minimize risk:

1. **Every 90 Days** (Recommended):
   - Create new access key in AWS Console
   - Update Cloud Stack Generator profile with new key
   - Delete old access key after verifying new one works
   - Mark calendar reminder for next rotation

2. **Immediate Rotation Required If**:
   - Key may have been exposed (e.g., accidentally committed to git)
   - Suspicious activity detected in AWS CloudTrail
   - Team member with key access leaves
   - Computer with stored keys is lost/stolen

### **Monitoring and Auditing**

#### **Enable CloudTrail Logging**
Track all API calls made by your IAM user:
1. AWS Console → **CloudTrail** → **Create trail**
2. Name: `cloud-stack-generator-audit`
3. Enable: ✅ Log file validation
4. Enable: ✅ SNS notification (optional - get alerts)
5. Review logs periodically for unexpected activity

#### **Set Up Billing Alerts**
Avoid surprise charges:
1. AWS Console → **Billing** → **Budgets**
2. Create budget: `CloudStackGenerator-Monthly`
3. Set threshold: `$10/month` (adjust based on usage)
4. Add email alert at 80% and 100%

#### **Review AWS Access Advisor**
Check which services the user actually accesses:
1. IAM → Users → Your user → **Access Advisor** tab
2. Review "Last accessed" dates
3. Remove permissions for unused services

### **IP-Based Access Restrictions (Advanced)**
Limit access keys to your IP address(es):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": [
            "YOUR.IP.ADDRESS.HERE/32",
            "OFFICE.IP.ADDRESS/32"
          ]
        }
      }
    }
  ]
}
```

**To find your IP**: Google "what is my ip" and add `/32` suffix.

### **Multi-Factor Authentication (MFA) for Root Account**
While not required for this IAM user, always enable MFA on your root AWS account:
1. AWS Console → Account dropdown → **Security Credentials**
2. **Multi-factor authentication (MFA)** → **Activate MFA**
3. Use authenticator app (Google Authenticator, Authy, etc.)

### **Least-Privilege Principle**
Only grant permissions actually needed:

- ✅ **DO**: Use custom policy with specific actions
- ✅ **DO**: Limit resource scope when possible
- ❌ **DON'T**: Use `*` for actions unless necessary
- ❌ **DON'T**: Attach `AdministratorAccess` policy

### **Secure Credential Backup**
If you downloaded the .csv file:
- ✅ Store in encrypted password manager (1Password, LastPass, Bitwarden)
- ✅ Encrypt file if storing locally (`7-Zip` with AES-256)
- ✅ Delete from Downloads folder after securing
- ❌ Don't email to yourself
- ❌ Don't store in cloud storage (Dropbox, Google Drive) unencrypted

### **Incident Response Plan**
If credentials are compromised:

1. **Immediately** - Delete compromised access key in AWS Console
2. **Review** - Check CloudTrail logs for unauthorized activity
3. **Rotate** - Create new access key and update application
4. **Audit** - Review S3 buckets for unexpected changes
5. **Report** - Contact AWS Support if fraudulent charges detected

---

## **🏢 Team/Organization Setup (Optional)**

### **For Multiple Users**
If multiple team members need access:

1. **Create individual IAM users** for each person
   - User naming: `cloudstack-firstname-lastname`
   - Each person gets their own access keys
   - Never share access keys between team members

2. **Use IAM Groups** for permission management:
   ```
   Group: CloudStackGeneratorUsers
   └── Policy: CloudStackGeneratorAccess
   └── Members: All team users
   ```

3. **Enable CloudTrail** to track who did what

4. **Implement key rotation policy** (e.g., quarterly)

### **For AWS Organizations**
If your company uses AWS Organizations:

1. Create dedicated AWS account for website hosting
2. Use cross-account roles instead of access keys
3. Implement Service Control Policies (SCPs) for governance
4. Centralize billing and cost allocation tags

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