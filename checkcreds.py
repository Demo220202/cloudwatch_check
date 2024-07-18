import argparse

parser = argparse.ArgumentParser(description="My Script Description")
parser.add_argument('--aws-access-key-id', required=True, help="AWS Access Key ID")
parser.add_argument('--aws-secret-access-key', required=True, help="AWS Secret Access Key")
    
args = parser.parse_args()

aws_access_key_id = args.aws_access_key_id
aws_secret_access_key = args.aws_secret_access_key

# Use the credentials as needed
print(f"AWS Access Key ID: {aws_access_key_id}")
print(f"AWS Secret Access Key: {aws_secret_access_key}")
