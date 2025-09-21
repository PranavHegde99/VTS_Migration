import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

def delete_fetched_rows(table_name, port):
    table = dynamodb.Table(table_name)

    try:
        # Fetch the item based on the provided PORT  Please mentiones required PORTs / partition key
        response = table.get_item(Key={'PORT': port})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"No data found for PORT {port}.")
            }

        item = response['Item']
        data_array = item['data']

        # Remove the rows where 'fetched' status is equals to True
        new_data_array = [entry for entry in data_array if not entry.get('fetched', False)]
        current_index = 0

        # Update the item in DynamoDB
        table.update_item(
            Key={'PORT': port},
            UpdateExpression="SET #data_alias = :new_data, currentIndex = :newIndex",
            ExpressionAttributeNames={
                '#data_alias': 'data' 
            },
            ExpressionAttributeValues={
                ':new_data': new_data_array,  #as Updated the data without fetched=True rows
                ':newIndex': current_index  # It will reset index value to 0
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": f"Deleted fetched rows and reset currentIndex for PORT {port}.",
                "remaining_data": new_data_array
            })
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to update item: {e.response['Error']['Message']}")
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

        # Delete fetched rows and reset the currentIndex
        return delete_fetched_rows(table_name, port)

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing request: {str(e)}")
        }
