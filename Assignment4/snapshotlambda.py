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

    print(f"Created snapshot: {snapshot_id}")

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
            print(f"Deleted old snapshot: {snap_id}")

    return {
        'statusCode': 200,
        'body': f"Snapshot {snapshot_id} created. Old snapshots cleaned up."
    }