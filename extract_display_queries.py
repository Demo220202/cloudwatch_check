import sys
import boto3
import json
import argparse

parser = argparse.ArgumentParser(description="Adding CloudWatch Metrics")
parser.add_argument('--aws-access-key-id', required=True, help="AWS Access Key ID")
parser.add_argument('--aws-secret-access-key', required=True, help="AWS Secret Access Key")
parser.add_argument('--domain', required=True, help="Domain name")
parser.add_argument('--region-name', required=True, help="AWS Region Name")

args = parser.parse_args()

# Fetch and print AWS credentials
aws_access_key_id = args.aws_access_key_id
aws_secret_access_key = args.aws_secret_access_key
region_name = args.region_name

# Capitalize the first letter of the domain name
source_identifier = args.domain.capitalize()[0]
source_identifier_fullname = args.domain
print(f"Source Identifier: {source_identifier_fullname}")

# Initialize a boto3 session
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

client = session.client('cloudwatch')

# Fetch all dashboards using pagination
dashboards = []
response = client.list_dashboards(
    DashboardNamePrefix='Zen_Error_Analysis'
)
dashboards.extend(response['DashboardEntries'])

print("Dashboard Names:")

list_all_dashboard = [dashboard['DashboardName'] for dashboard in dashboards]

print(list_all_dashboard)

titles_to_skip = ["SSO Conf Error"]

dashboard_use = ""

for dashboard in list_all_dashboard:
    if len(dashboard) == 25:
        if source_identifier >= dashboard[19] and source_identifier <= dashboard[24]:
            dashboard_use = dashboard
    elif len(dashboard) == 20:
        if source_identifier == dashboard[19]:
            dashboard_use = dashboard

print(dashboard_use)

try:
    response = client.get_dashboard(DashboardName=dashboard_use)
    dashboard_body = json.loads(response['DashboardBody'])
except client.exceptions.ResourceNotFoundException:
    print(f"Dashboard {dashboard_use} does not exist.")
    exit(1)

updated = False

# Count the max source for the check
maxCountSource = 0
for widget in dashboard_body.get('widgets', []):
    count_source = 0
    if widget['type'] == 'log':
        # For skipping the title that is not required
        if widget['properties'].get('title') not in titles_to_skip:
            query = widget['properties'].get('query', '')

            query_in_list = query.split(' | ')

            # Check no of sources
            for components in query_in_list:
                if "SOURCE" in components:
                    count_source = count_source + 1

            maxCountSource = max(maxCountSource, count_source)

print("Maximum number of sources till now : ", maxCountSource)

# Only if all the widgets have sources less than 50
if maxCountSource < 50:
    for widget in dashboard_body.get('widgets', []):
        print()
        count_source = 0
        new_source = f"SOURCE 'PhpAppLogs_{source_identifier_fullname}'"
        if widget['type'] == 'log':
            # For skipping the title that is not required
            if widget['properties'].get('title') not in titles_to_skip:
                query = widget['properties'].get('query', '')
                print(f"Old Query: {query}")

                query_in_list = query.split(' | ')
                
                print("\nQuery in list format: ", query_in_list)

                for components in query_in_list:
                    if "SOURCE" in components:
                        count_source = count_source + 1
                
                if new_source not in query_in_list:  # If it does not already exist
                    query_in_list.insert(count_source, new_source) # Replace 0 by count_source, if you want to see the latest log group at the top

                    print("\nNew Query in list format: ", query_in_list)

                    new_query = ' | '.join(query_in_list)
                    print("\nNew Query: ", new_query)

                    widget['properties']['query'] = new_query
                    updated = True
                    print(widget['properties'].get('title'), "updated")

                else:
                    print(widget['properties'].get('title'), "not updated")

print()
if not updated:
    print("No widgets were updated.")

print()
updated_dashboard_body = json.dumps(dashboard_body)

# Save the updated dashboard body and dashboard_use to a file
with open("dashboard_update_info.json", "w") as f:
    json.dump({
        "dashboard_name": dashboard_use,
        "updated_dashboard_body": updated_dashboard_body
    }, f)
