import boto3
import pytz
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
PRICE_SPIKE_THRESHOLD = 150
AEST = pytz.timezone("Australia/Sydney")

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

from datetime import datetime, timezone

def detect_price_spike():
    try:
        logger.info("Detecting price spike...")

        response = forecast_table.scan()
        if "Items" not in response or not response["Items"]:
            return {"statusCode": 404, "body": json.dumps("No forecast data found.")}

        df = pd.DataFrame(response["Items"])
        df["SETTLEMENTDATE"] = pd.to_datetime(df["SETTLEMENTDATE"], errors="coerce").dt.tz_localize(None)  # Make it naive
        df["RRP"] = df["RRP"].astype(float)

        current_time = datetime.now(AEST)

        df = df[df["SETTLEMENTDATE"] > current_time]
        print(df)

        spike = df[df["RRP"] > PRICE_SPIKE_THRESHOLD].sort_values("SETTLEMENTDATE").head(1)

        if spike.empty:
            return {"statusCode": 200, "body": json.dumps("No price spike detected for the rest of the day")}

        spike_time = spike.iloc[0]["SETTLEMENTDATE"].strftime("%Y-%m-%d %H:%M:%S")

        return {
            "statusCode": 200,
            "body": json.dumps(f"A price spike is expected at {spike_time}.")
        }
    except Exception as e:
        logger.error(f"Error detecting price spike: {str(e)}")
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
    query_type = event.get('queryType')

    if query_type == "forecast":
        return fetch_forecast_data()
    elif query_type == "metadata":
        return fetch_latest_model_metadata()
    elif query_type == "spike":
        return detect_price_spike()
    else:
        return {"statusCode": 400, "body": json.dumps("Invalid query type. Use 'forecast', 'metadata', or 'spike'.")}

print(detect_price_spike())