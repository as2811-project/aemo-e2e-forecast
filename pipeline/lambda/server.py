import boto3
import json
import os
import logging
import pandas as pd
import plotly
import plotly.express as px
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize AWS services
dynamodb = boto3.resource("dynamodb")
table_name = os.getenv("DDB_TABLE")
table = dynamodb.Table(table_name)

# Helper class to handle Decimal serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    """
    AWS Lambda function to fetch forecast and actual data from DynamoDB,
    convert it into a Plotly JSON object, and return it.

    Steps:
    1. Query the DynamoDB table for all stored data.
    2. Convert the data into a Pandas DataFrame.
    3. Separate actuals and forecasts into different series.
    4. Generate a Plotly figure with distinct lines.
    5. Return the figure as a JSON response.

    Error Handling:
    - Logs errors and returns an HTTP 500 response if fetching fails.
    """
    try:
        logger.info("Fetching data from DynamoDB...")
        response = table.scan()

        if "Items" not in response or not response["Items"]:
            return {"statusCode": 404, "body": json.dumps("No data found")}

        df = pd.DataFrame(response["Items"])
        print("Created dataframe from DynamoDB")
        df["SETTLEMENTDATE"] = pd.to_datetime(df["SETTLEMENTDATE"])
        print("Converted settlement date to datetime")
        df = df.sort_values(by="SETTLEMENTDATE")
        print("Sorted by date time")
        fig = px.line(df, x="SETTLEMENTDATE", y="RRP", color='PeriodType')
        print("Created plotly figure")
        plotly_json = plotly.io.to_json(fig)

        return {"statusCode": 200, "body": plotly_json}

    except Exception as e:
        logger.error(f"Error fetching or processing data: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}