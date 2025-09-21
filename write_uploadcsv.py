import json
import boto3
import csv
import io
import urllib.parse
import urllib.request
from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ATLASSIAN')  # Change this to your actual table name

def lambda_handler(event, context):
    try:
        # Extract port from the query string parameters Based on the requirements
        port = event['queryStringParameters']['port']
        
        # Read the CSV data from the event body
        file_content = event['body']
        
        data = []
        csv_reader = csv.DictReader(io.StringIO(file_content))
        
        for row in csv_reader:
            data.append(row)  # Append the row directly

        # Prepare the payload for the existing API
        payload = {
            "PORT": port,
            "data": data
        }
        
        # Check if the data exists for the specified port
        if not check_data_exists(port):
            # If no data exists, create a new entry in DynamoDB
            create_entry(port, data)

        # Call the existing API to push data
        response = push_data_to_existing_api(payload)
        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal Server Error: {str(e)}")
        }

def check_data_exists(port):
    """Check if data exists for the given port in DynamoDB."""
    try:
        response = table.get_item(Key={'PORT': port})
        return 'Item' in response
    except ClientError as e:
        print(f"Error fetching item: {e.response['Error']['Message']}")
        return False

def create_entry(port, data):
    """Create a new entry in DynamoDB for the specified port."""
    item = {
        'PORT': port,
        'data': data
    }
    try:
        table.put_item(Item=item)
        print(f"New entry created for PORT: {port}")
    except ClientError as e:
        print(f"Failed to create item: {e.response['Error']['Message']}")

def push_data_to_existing_api(payload):
    existing_api_url = "https://w3enfolfkb.execute-api.eu-west-2.amazonaws.com/pushdata"
    
    try:
        # Prepare the data for the POST request
        data = json.dumps(payload).encode('utf-8')  # Convert the payload to JSON and encode
        headers = {'Content-Type': 'application/json'}

        # Create a request object
        req = urllib.request.Request(existing_api_url, data=data, headers=headers, method='POST')
        
        # Send the request and read the response
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            return {
                'statusCode': response.getcode(),
                'body': response_body
            }

    except Exception as e:
        print(f"Error calling existing API: {str(e)}") # Error handling
        return {
            'statusCode': 500,
            'body': f'Error calling existing API: {str(e)}'
        }
