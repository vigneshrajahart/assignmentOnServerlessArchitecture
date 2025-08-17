# Automated S3 Bucket Cleanup Using AWS Lambda and Boto3

## 📌 Objective

Automate the deletion of files older than **30 days** in a specific S3 bucket using **AWS Lambda** and **Boto3**.

---

## 🛠️ Step 1: S3 Setup

1. Go to the **AWS Management Console → S3**.
2. Click **Create bucket** → Give it a unique name (example: `my-s3-cleanup-bucket`).
3. Leave other settings as default → Click **Create bucket**.
4. Upload multiple files into the bucket.

   * For testing: Upload some files now (consider them as *new*).
   * To simulate old files:

     * Use prefixes like `old/` for files you want treated as older.
     * Or temporarily adjust the Lambda script to delete files older than 0 days.

---

## 🛠️ Step 2: IAM Role for Lambda

1. Navigate to **IAM → Roles → Create Role**.

2. Select **AWS Service → Lambda**.

3. Attach the policy **AmazonS3FullAccess**.

   > ⚠️ For real-world use, create a restrictive inline policy (example below).

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:ListBucket",
           "s3:GetObject",
           "s3:DeleteObject"
         ],
         "Resource": [
           "arn:aws:s3:::my-s3-cleanup-bucket",
           "arn:aws:s3:::my-s3-cleanup-bucket/*"
         ]
       }
     ]
   }
   ```

4. Name the role `LambdaS3CleanupRole`.

5. Click **Create Role**.

---

## 🛠️ Step 3: Create Lambda Function

1. Navigate to **Lambda → Create function**.

2. Choose:

   * Author from scratch
   * Runtime: **Python 3.x**
   * Execution role: **Use existing role** → Select `LambdaS3CleanupRole`

3. Inside the **code editor**, paste the following script:

   ```python
   import boto3
   import datetime

   s3 = boto3.client('s3')
   BUCKET_NAME = 'my-s3-cleanup-bucket'  # Replace with your bucket name
   DAYS_THRESHOLD = 30

   def lambda_handler(event, context):
       today = datetime.datetime.now(datetime.timezone.utc)
       cutoff_date = today - datetime.timedelta(days=DAYS_THRESHOLD)

       response = s3.list_objects_v2(Bucket=BUCKET_NAME)

       if 'Contents' not in response:
           print("Bucket is empty")
           return

       for obj in response['Contents']:
           key = obj['Key']
           last_modified = obj['LastModified']

           if last_modified < cutoff_date:
               print(f"Deleting {key}, LastModified: {last_modified}")
               s3.delete_object(Bucket=BUCKET_NAME, Key=key)

       print("Cleanup complete.")
   ```

4. Click **Deploy**.

---

## 🛠️ Step 4: Manual Invocation & Testing

1. In the Lambda function page → Click **Test** → Configure test event (use default settings).
2. Click **Test** again to run.
3. Go to **S3 bucket → Objects**.

   * Verify that files older than 30 days are deleted.
   * New files remain intact.

---

## ✅ Notes & Best Practices

* **Testing Tip**: Change `DAYS_THRESHOLD = 0` to delete all files immediately (useful for testing).
* **CloudWatch Logs**: Check logs in **CloudWatch → Log Groups → Lambda Logs** for debugging.
* **Real-World Alternative**: Use **S3 Lifecycle Rules** for automated cleanup (recommended for production).

---

## 📂 Repository Structure

```
aws-s3-cleanup-lambda/
│── README.md   # Documentation (this file)
│── lambda_s3_cleanup.py  # Python code (optional if keeping separate)
```

---

## 🎯 Outcome

* You now have an automated Lambda function that cleans up S3 files older than 30 days.
* This setup can be extended with **CloudWatch Events** to run daily.
