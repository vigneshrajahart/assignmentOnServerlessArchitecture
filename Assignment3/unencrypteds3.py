import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    try:
        # List all buckets
        response = s3.list_buckets()
        buckets = response['Buckets']
        
        unencrypted_buckets = []
        
        for bucket in buckets:
            bucket_name = bucket['Name']
            try:
                # Check encryption configuration
                enc = s3.get_bucket_encryption(Bucket=bucket_name)
                rules = enc['ServerSideEncryptionConfiguration']['Rules']
                
                print(f"✅ Bucket '{bucket_name}' has encryption enabled: {rules}")
            
            except ClientError as e:
                # If no encryption, log the bucket name
                if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                    print(f"Bucket '{bucket_name}' has NO encryption")
                    unencrypted_buckets.append(bucket_name)
                else:
                    print(f" Could not check bucket '{bucket_name}': {e}")
        
        # Final result logging
        if unencrypted_buckets:
            print("\n🔎 Buckets without encryption:")
            for b in unencrypted_buckets:
                print(f" - {b}")
        else:
            print("\n✅ All buckets have encryption enabled.")
    
    except Exception as e:
        print(f"Error: {str(e)}")