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

dynamodb = boto3.resource("dynamodb")
forecast_table = dynamodb.Table(os.getenv("DDB_TABLE"))
metadata_table = dynamodb.Table("model-metadata")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def fetch_forecast_data():
    try:
        logger.info("Fetching forecast data from DynamoDB...")
        response = forecast_table.scan()

        if "Items" not in response or not response["Items"]:
            return {"statusCode": 404, "body": json.dumps("No forecast data found")}

        df = pd.DataFrame(response["Items"])
        df["SETTLEMENTDATE"] = pd.to_datetime(df["SETTLEMENTDATE"])
        df = df.sort_values(by="SETTLEMENTDATE")

        fig = px.line(df, x="SETTLEMENTDATE", y="RRP", color='PeriodType')
        plotly_json = plotly.io.to_json(fig)

        return {"statusCode": 200, "body": plotly_json}
    except Exception as e:
        logger.error(f"Error fetching forecast data: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}


def fetch_latest_model_metadata():
    try:
        logger.info("Fetching latest model metadata...")
        response = metadata_table.scan()

        if "Items" not in response or not response["Items"]:
            return {"statusCode": 404, "body": json.dumps("No metadata found")}

        latest_metadata = max(response["Items"], key=lambda x: x["training_date"])
        return {"statusCode": 200, "body": json.dumps(latest_metadata, cls=DecimalEncoder)}
    except Exception as e:
        logger.error(f"Error fetching model metadata: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}


def lambda_handler(event, context):
    query_type = event.get("queryType", "forecast")  # Default to forecast if not specified

    if query_type == "forecast":
        return fetch_forecast_data()
    elif query_type == "metadata":
        return fetch_latest_model_metadata()
    else:
        return {"statusCode": 400, "body": json.dumps("Invalid query type. Use 'forecast' or 'metadata'.")}
