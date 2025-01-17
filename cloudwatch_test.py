import boto3
import json
import getpass
import argparse

parser = argparse.ArgumentParser(description="My Script Description")
parser.add_argument('--aws-access-key-id', required=True, help="AWS Access Key ID")
parser.add_argument('--aws-secret-access-key', required=True, help="AWS Secret Access Key")
    
args = parser.parse_args()

# Prompt for AWS credentials
aws_access_key_id = args.aws_access_key_id
aws_secret_access_key = args.aws_secret_access_key

# Use the credentials as needed
print(f"AWS Access Key ID: {aws_access_key_id}")
print(f"AWS Secret Access Key: {aws_secret_access_key}")


region_name = 'us-west-1'  # Replace with your desired region

# Initialization of a session(boto3) with giving creds from your end
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

client = session.client('cloudwatch')

# Fetch all dashboards using pagination
dashboards = []
response = client.list_dashboards()
dashboards.extend(response['DashboardEntries'])

while 'NextToken' in response:
    response = client.list_dashboards(NextToken=response['NextToken'])
    dashboards.extend(response['DashboardEntries'])

# Print the names of all dashboards
list_all_dashboard = [] # having all the dashboards with the prefix Zen_Error_Analysis

print("Dashboard Names:")
for dashboard in dashboards:
    if dashboard['DashboardName'].startswith("Zen_Error_Analysis"):
        print(dashboard['DashboardName'])
        list_all_dashboard.append(dashboard['DashboardName'])

print(list_all_dashboard)

new_source = "SOURCE 'demo-jenkins-logs'"
title_to_skip = "SSO Conf Error"
source_identifier = new_source[8].upper()
# source_identifier = new_source.split("PhpAppLogs_")[1][0].upper()

print(source_identifier) # debugging purpose

dashboard_use = ""

for dashboard in list_all_dashboard:
    if len(dashboard) == 25:
        # print(dashboard, dashboard[19], dashboard[24])
        if source_identifier >= dashboard[19] and source_identifier <= dashboard[24]:
            # print(dashboard)
            dashboard_use = dashboard
    elif len(dashboard) == 20: # Single Letter brandname
        if source_identifier >= dashboard[19]:
            dashboard_use = dashboard

print(dashboard_use)

# Yahan tak I got the dashboard_name jiske widgets mein mujhe daalna hai, cool

try:
    response = client.get_dashboard(DashboardName=dashboard_use)
    dashboard_body = json.loads(response['DashboardBody'])
except client.exceptions.ResourceNotFoundException:
    print(f"Dashboard {dashboard_use} does not exist.")
    exit(1)

updated = False
count_source = 0

for widget in dashboard_body.get('widgets', []):
    if widget['type'] == 'log':
        # For skipping the title that is not required
        if widget['properties'].get('title') != title_to_skip:
            query = widget['properties'].get('query', '')
            print(f"Old Query: {query}")

            query_in_list = query.split(' | ')
            print(query_in_list)

            # Check no of sources

            for components in query_in_list :
                if "SOURCE" in components:
                    count_source = count_source + 1

            print(count_source)

            if count_source < 50 : # Ab safe hai karna
                if new_source not in query_in_list: # Agar wo pehle se exist nahi karta hoga to
                    query_in_list.insert(count_source, new_source)

                print(query_in_list)

                new_query = ' | '.join(query_in_list)
                print(new_query)

                widget['properties']['query'] = new_query
                updated = True



if not updated:
    print("No widgets were updated.")


updated_dashboard_body = json.dumps(dashboard_body)

# Step 3: Update the dashboard with the modified widgets i.e., the new added log group
try:
    response = client.put_dashboard(
        DashboardName=dashboard_use,
        DashboardBody=updated_dashboard_body
    )
    print("Dashboard updated successfully")
    print(response)
except Exception as e:
    print(f"An error occurred while updating the dashboard: {e}")
