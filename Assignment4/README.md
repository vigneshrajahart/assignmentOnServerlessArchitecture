# Assignment 4: Automatic EBS Snapshot and Cleanup Using AWS Lambda and Boto3

## 🎯 Objective
Automate the backup process for EBS volumes by creating snapshots and cleaning up snapshots older than 30 days.  
This helps in maintaining backups while optimizing costs.

---

## ✅ Prerequisites
- An **AWS account** with permissions for EC2, IAM, Lambda, and CloudWatch.
- At least one **EBS volume** attached to an instance.
- Basic knowledge of **Python and AWS Console**.

---

## 📝 Step 1: Identify/Create an EBS Volume
1. Navigate to **EC2 Dashboard → Volumes**.
2. Select an existing EBS volume or create a new one.
3. Copy the **Volume ID** (e.g., `vol-0abcd1234ef56789`).

---

## 🛡️ Step 2: Create IAM Role for Lambda
1. Navigate to **IAM → Roles → Create Role**.
2. Select **Lambda** as the trusted entity.
3. Attach the following IAM policy (least privilege recommended):


{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateSnapshot",
        "ec2:DeleteSnapshot",
        "ec2:DescribeSnapshots",
        "ec2:DescribeVolumes",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}


⚙️ Step 3: Create Lambda Function

Go to AWS Lambda → Create Function.

Choose Author from scratch.

Runtime: Python 3.x.

Assign the IAM role LambdaEbsBackupRole.

Paste the following Python code:

import boto3
from datetime import datetime, timedelta, timezone

# Configuration
VOLUME_ID = "vol-0abcd1234ef56789"  # Replace with your EBS Volume ID
RETENTION_DAYS = 30

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Step 1: Create snapshot
    description = f"Automated snapshot for {VOLUME_ID} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    snapshot = ec2.create_snapshot(
        VolumeId=VOLUME_ID,
        Description=description
    )

    snapshot_id = snapshot['SnapshotId']

    # Tag the snapshot
    ec2.create_tags(
        Resources=[snapshot_id],
        Tags=[
            {'Key': 'CreatedBy', 'Value': 'LambdaEbsBackup'},
            {'Key': 'VolumeId', 'Value': VOLUME_ID}
        ]
    )

    print(f"✅ Created snapshot: {snapshot_id}")

    # Step 2: Delete old snapshots
    old_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

    snapshots = ec2.describe_snapshots(
        Filters=[
            {'Name': 'volume-id', 'Values': [VOLUME_ID]},
            {'Name': 'tag:CreatedBy', 'Values': ['LambdaEbsBackup']}
        ],
        OwnerIds=['self']
    )['Snapshots']

    for snap in snapshots:
        start_time = snap['StartTime']
        snap_id = snap['SnapshotId']
        if start_time < old_date:
            ec2.delete_snapshot(SnapshotId=snap_id)
            print(f"🗑️ Deleted old snapshot: {snap_id}")

    return {
        'statusCode': 200,
        'body': f"Snapshot {snapshot_id} created. Old snapshots cleaned up."
    }

🧪 Step 4: Test the Function

Save and Deploy the Lambda function.

Go to Test → Configure Test Event → Create a dummy test event.

Run the function.

Check execution results in CloudWatch Logs.

Verify new snapshot in EC2 → Snapshots.

⏱️ Step 5: Automate with CloudWatch Events (Bonus)

Navigate to CloudWatch → Rules → Create Rule.

Choose Schedule → Cron expression (e.g., cron(0 0 ? * 1 *) = every Sunday at midnight).

Add your Lambda function as the Target.

Save the rule.

🔍 Verification

New snapshots appear after Lambda runs.

Old snapshots (>30 days) are automatically deleted.

CloudWatch Logs confirm snapshot creation & deletion.