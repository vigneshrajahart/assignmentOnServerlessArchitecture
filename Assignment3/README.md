# Assignment 3: Monitor Unencrypted S3 Buckets Using AWS Lambda and Boto3

## 🎯 Objective
Enhance AWS security posture by setting up a **Lambda function** that detects any **S3 bucket without server-side encryption (SSE)** enabled.

This automation helps ensure compliance and prevents sensitive data from being stored in unencrypted S3 buckets.

---

## 🛠️ Steps to Implement

### 1. S3 Setup
1. Navigate to **AWS Console → S3 → Buckets → Create bucket**.
2. Create a few buckets:
   - **Encrypted bucket:** Enable server-side encryption (AES-256 or KMS).
   - **Unencrypted buckets:** Leave encryption disabled.
3. (Optional) Upload test files into the buckets.

---

### 2. Create IAM Role for Lambda
1. Go to **IAM → Roles → Create Role**.
2. Select **Lambda** as the trusted entity.
3. Attach policy:  
   - `AmazonS3ReadOnlyAccess`
4. Name the role: **`LambdaS3ReadOnlyRole`**

---

### 3. Create Lambda Function
1. Go to **Lambda → Functions → Create Function**.
2. Choose:
   - **Author from scratch**
   - Runtime: **Python 3.x**
   - Function name: `DetectUnencryptedBuckets`
   - Execution role: **Use existing role** → `LambdaS3ReadOnlyRole`
3. Click **Create Function**.

---

### 4. Add Python Script
Paste the following code inside the Lambda code editor:

```python
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    try:
        response = s3.list_buckets()
        buckets = response['Buckets']
        
        unencrypted_buckets = []
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            try:
                enc = s3.get_bucket_encryption(Bucket=bucket_name)
                rules = enc['ServerSideEncryptionConfiguration']['Rules']
                print(f"✅ Bucket '{bucket_name}' has encryption enabled: {rules}")
            
            except ClientError as e:
                if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                    print(f"❌ Bucket '{bucket_name}' has NO encryption")
                    unencrypted_buckets.append(bucket_name)
                else:
                    print(f"⚠️ Could not check bucket '{bucket_name}': {e}")
        
        if unencrypted_buckets:
            print("\n🔎 Buckets without encryption:")
            for b in unencrypted_buckets:
                print(f" - {b}")
        else:
            print("\n✅ All buckets have encryption enabled.")
    
    except Exception as e:
        print(f"Error: {str(e)}")
