import boto3
import datetime

s3 = boto3.client('s3')
BUCKET_NAME = 'my-s3-cleanup-bucket'  
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