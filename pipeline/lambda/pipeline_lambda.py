from datetime import datetime
import boto3
import requests
import json
import io
import pandas as pd
import os

API_URL = "https://visualisations.aemo.com.au/aemo/apps/api/report/5MIN"
S3_BUCKET = os.environ.get('S3_BUCKET')

def lambda_handler(event, context):
    try:
        print(f"Hitting endpoint: {API_URL}")

        payload = json.dumps({
            "timescale": ["30MIN"]
        })

        response = requests.post(API_URL, data=payload)
        response.raise_for_status()  # Raise exception for non-200 status codes

        data = response.json()
        intervals = data["5MIN"]
        intervals_df = pd.DataFrame(intervals)

        intervals_df = intervals_df.query('REGION == "VIC1" & PERIODTYPE == "ACTUAL"')

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data_{timestamp}.csv"

        csv_buffer = io.StringIO()
        intervals_df.to_csv(csv_buffer, header=True, index=False)

        s3_client = boto3.client('s3')
        s3_key = f"landing-zone/{filename}"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=csv_buffer.getvalue()
        )

        print(f"Successfully uploaded {filename} to S3 bucket {S3_BUCKET}")

        return {
            'statusCode': 200,
            'body': f"Data from the last 24 hours stored to S3 as CSV: {filename}"
        }

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"API request failed: {str(e)}"
        }
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error processing data: {str(e)}"
        }