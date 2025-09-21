import json
import boto3
from botocore.exceptions import ClientError

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')

def write_data(PORT, data):
    table = dynamodb.Table('ATLASSIAN')
    item = {
        'PORT': PORT,
        'data': data
    }
    try:
        table.put_item(Item=item)
        return {
            'statusCode': 200,
            'body': json.dumps(f'Item {item} written to table VTS.')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Failed to write item: {e.response["Error"]["Message"]}')
        }

def lambda_handler(event, context):
    try:
        # event already contains the parsed JSON from VTSDataHandler
        PORT = event['PORT']
        data = event['data']
        return write_data(PORT, data)
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error processing request: {str(e)}')
        }
