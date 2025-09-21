import boto3
import csv
import json
import io
from botocore.exceptions import ClientError

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Table name
TABLE_NAME = 'ATLASSIAN'  # Replace with your table name

def fetch_data_from_dynamodb(PORT):
    """
    Fetch the data for the given PORT from the DynamoDB table.
    """
    table = dynamodb.Table(TABLE_NAME)
    try:
        response = table.get_item(Key={'PORT': PORT})
        if 'Item' in response:
            return response['Item']['data']  # Return the data array
        else:
            raise Exception(f"Data not found for PORT: {PORT}")
    except ClientError as e:
        raise Exception(f"Failed to fetch data from DynamoDB: {e.response['Error']['Message']}")

def create_csv_content(data):
    """
    Convert the list of dictionaries to CSV format.
    """
    csv_buffer = io.StringIO()
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
    
    csv_writer.writeheader()
    for row in data:
        csv_writer.writerow(row)
    
    return csv_buffer.getvalue()

def lambda_handler(event, context):
    """
    Lambda function entry point.
    """
    try:
        # Extract PORT from the query string parameters
        PORT = event.get('queryStringParameters', {}).get('PORT')
        if not PORT:
            return {
                'statusCode': 400,
                'body': json.dumps("Missing 'PORT' parameter in the request.")
            }

        # Fetch data from DynamoDB for the given PORT
        data = fetch_data_from_dynamodb(PORT)
        
        # Generate CSV content from the data
        csv_content = create_csv_content(data)
        
        # Return the CSV as a file download
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename="port_{PORT}_data.csv"'
            },
            'body': csv_content
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
