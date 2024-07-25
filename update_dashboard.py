import sys
import boto3
import json
import argparse

parser = argparse.ArgumentParser(description="Update CloudWatch Dashboard")
parser.add_argument('--aws-access-key-id', required=True, help="AWS Access Key ID")
parser.add_argument('--aws-secret-access-key', required=True, help="AWS Secret Access Key")
parser.add_argument('--region-name', required=True, help="AWS Region Name")

args = parser.parse_args()

# Fetch and print AWS credentials
aws_access_key_id = args.aws_access_key_id
aws_secret_access_key = args.aws_secret_access_key
region_name = args.region_name

# Initialize a boto3 session
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

client = session.client('cloudwatch')

# Read the updated dashboard body and dashboard name from the file
with open("dashboard_update_info.json", "r") as f:
    update_info = json.load(f)
    updated_dashboard_body = update_info["updated_dashboard_body"]
    dashboard_name = update_info["dashboard_name"]

# Step 3: Update the dashboard with the modified widgets
try:
    response = client.put_dashboard(
        DashboardName=dashboard_name,
        DashboardBody=updated_dashboard_body
    )
    print("Dashboard updated successfully\n")
    print(response)
except Exception as e:
    print(f"An error occurred while updating the dashboard: {e}")
