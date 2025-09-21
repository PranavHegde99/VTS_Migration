import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) 
        return super(DecimalEncoder, self).default(obj)

def fetch_data(table_name, port):
    table = dynamodb.Table(table_name)

    try:
        # Fetch the item based on the provided PORT (partition key)
        response = table.get_item(Key={'PORT': port})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"No data found for PORT {port}.")
            }

        item = response['Item']
        data_array = item['data']
        
        # Find the first index where fetched is False
        current_index = next((index for index, entry in enumerate(data_array) if not entry.get('fetched', False)), None)

        # If all items are fetched, return an appropriate message
        if current_index is None:
            return {
                'statusCode': 404,
                'body': json.dumps("No more data to fetch.")
            }

        # Fetch the current data item and mark it as fetched
        current_data = data_array[current_index]
        current_data['fetched'] = True

        table.update_item(
            Key={'PORT': port},
            UpdateExpression="SET #data_alias = :data",
            ExpressionAttributeNames={
                '#data_alias': 'data'  # Alias for the reserved keyword 'data'
            },
            ExpressionAttributeValues={
                ':data': data_array  # Update the entire data array with the modified fetched statuses
            }
        )

        # Return success with the current index
        return {
            'statusCode': 200,
            'body': json.dumps({
                "PORT": port,
                "data": current_data,
                "currentIndex": current_index  # Return the current index that was fetched
            }, cls=DecimalEncoder)  # Use custom encoder for Decimal
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to fetch/update item: {e.response['Error']['Message']}")
        }

def lambda_handler(event, context):
    try:
        # Extract table name and PORT from the query string parameters
        table_name = event['queryStringParameters'].get('tableName')
        port = event['queryStringParameters'].get('PORT')

        if not table_name or not port:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing tableName or PORT in query string parameters.')
            }

        # Fetch and return data for the specified PORT and table
        return fetch_data(table_name, port)

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing request: {str(e)}")
        }
