# 🚀 Automated Instance Management Using AWS Lambda and Boto3

## 🎯 Objective
This project automates the **starting and stopping of EC2 instances** based on tags using **AWS Lambda + Boto3**.  

- Instances tagged with `Action=Auto-Stop` → **Stopped automatically**  
- Instances tagged with `Action=Auto-Start` → **Started automatically**  

---

## 📌 Prerequisites
- AWS Account (Free Tier eligible)  
- IAM User with permissions to create EC2, Lambda, and IAM Roles  
- Basic knowledge of Python and AWS Console  

---

## 🛠️ Step 1: Launch EC2 Instances

1. Navigate to **AWS Console → EC2 → Instances → Launch Instance**  
2. Choose:  
   - **Amazon Linux 2 AMI** (or any available free-tier AMI)  
   - **t2.micro** (Free tier eligible)  
   - Default storage and network settings  
3. Launch **two instances**  
4. Apply tags:  
   - Instance 1:  
     - **Key:** `Action`  
     - **Value:** `Auto-Stop`  
   - Instance 2:  
     - **Key:** `Action`  
     - **Value:** `Auto-Start`  

✅ Now you have two instances with tags  

---

## 🛠️ Step 2: Create IAM Role for Lambda

1. Go to **IAM → Roles → Create Role**  
2. Trusted Entity → **AWS Service** → Choose **Lambda**  
3. Attach Policy:  
   - `AmazonEC2FullAccess` (✅ For learning; in production use least-privilege)  
4. Name the role: `LambdaEC2Role`  
5. Create the role  

---

## 🛠️ Step 3: Create Lambda Function

1. Go to **AWS Lambda → Create Function**  
2. Choose:  
   - Author from scratch  
   - Runtime: **Python 3.x**  
   - Execution Role: **LambdaEC2Role** (created in Step 2)  
3. Paste the following code in the Lambda editor:

```python
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Find and stop instances with Action=Auto-Stop
    stop_instances = ec2.describe_instances(
        Filters=[{'Name': 'tag:Action', 'Values': ['Auto-Stop']}]
    )
    stop_ids = [
        instance['InstanceId']
        for reservation in stop_instances['Reservations']
        for instance in reservation['Instances']
    ]
    if stop_ids:
        ec2.stop_instances(InstanceIds=stop_ids)
        print(f"Stopped instances: {stop_ids}")
    else:
        print("No instances found with tag Auto-Stop")

    # Find and start instances with Action=Auto-Start
    start_instances = ec2.describe_instances(
        Filters=[{'Name': 'tag:Action', 'Values': ['Auto-Start']}]
    )
    start_ids = [
        instance['InstanceId']
        for reservation in start_instances['Reservations']
        for instance in reservation['Instances']
    ]
    if start_ids:
        ec2.start_instances(InstanceIds=start_ids)
        print(f"Started instances: {start_ids}")
    else:
        print("No instances found with tag Auto-Start")

    return {
        'statusCode': 200,
        'body': f"Stopped: {stop_ids}, Started: {start_ids}"
    }

    🛠️ Step 4: Test the Lambda Function

In Lambda console, click Test → Configure Test Event

Choose a Blank event template (default JSON is fine)

Run the test

Check logs in CloudWatch or Lambda output

🛠️ Step 5: Verify in EC2 Console

Instance with Action=Auto-Stop → Stopped

Instance with Action=Auto-Start → Running

✅ Task completed successfully!

📖 Summary

Created two EC2 instances with tags

Built a Lambda function with Boto3 to start/stop EC2 instances

Assigned IAM role with EC2 access

Tested via manual invocation
