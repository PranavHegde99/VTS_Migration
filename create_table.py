import boto3
from botocore.exceptions import ClientError
import time

def lambda_handler(event, context):
    # TableName = event['queryStringParameters']['TableName']
    # Initialize the DynamoDB client 
    # if yopu're planning to pass in String/ endpoint
    dynamodb = boto3.client('dynamodb')

    try:
        # table_name = event['queryStringParameters'].get('tablename')
        
        # if not table_name:
        #     return {
        #         'statusCode': 400,
        #         'body': json.dumps({'message': 'tablename is required as a query parameter'})
        #     }
        # Create the DynamoDB table
        response = dynamodb.create_table(
            TableName='ATLASSIAN',
            KeySchema=[
                {
                    'AttributeName': 'PORT',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PORT',
                    'AttributeType': 'S'  # String type
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
           
        # Wait for the table to be created added Sleep time
        table_name = response['TableDescription']['TableName']
        print(f'Table creation initiated for: {table_name}')


        dynamodb_resource = boto3.resource('dynamodb')
        table = dynamodb_resource.Table(table_name)
        table.wait_until_exists()
        print('Table VTS created successfully.')
        
        return {
            'statusCode': 200,
            'body': f'Table {table_name} created successfully.'
        }
      # Added error handling  
    except ClientError as e:
        error_message = f'Failed to create table: {e.response["Error"]["Message"]}'
        print(error_message)
        return {
            'statusCode': 400,
            'body': error_message
        }
    except Exception as e:
        error_message = f'An error occurred: {str(e)}'
        print(error_message)
        return {
            'statusCode': 500,
            'body': error_message
        }
