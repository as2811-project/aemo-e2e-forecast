import boto3
import json
import os
import logging
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv("DDB_TABLE")
table = dynamodb.Table(table_name)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    """
    AWS Lambda function to fetch forecast and actual data from DynamoDB
    and return it as JSON.

    Steps:
    1. Query the DynamoDB table for all stored data.
    2. Return the results as a JSON response.

    Error Handling:
    - Logs errors and returns an HTTP 500 response if fetching fails.
    """
    try:
        logger.info("Fetching data from DynamoDB...")
        response = table.scan()

        if 'Items' not in response:
            return {'statusCode': 404, 'body': json.dumps('No data found')}

        results = response['Items']
        results.sort(key=lambda x: x['SETTLEMENTDATE'], reverse=False)
        return {'statusCode': 200, 'body': json.dumps(results, cls=DecimalEncoder)}

    except Exception as e:
        logger.error(f"Error fetching data from DynamoDB: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}