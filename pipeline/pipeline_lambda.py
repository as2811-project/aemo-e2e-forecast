from datetime import datetime

import boto3
import requests
import json
import io
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

API_URL = os.getenv("API_URL")
payload = json.dumps({
  "timescale": [
    "30MIN"
  ]
})

def lambda_handler(event, context):
    print("Hit the endpoint: ", API_URL)
    response = requests.post(API_URL, data=payload)
    data = response.json()
    intervals = data["5MIN"]
    intervals_df = pd.DataFrame(intervals)

    intervals_df.query('REGION == "VIC1" & PERIODTYPE == "ACTUAL"').to_csv(f'{datetime.now()}.csv',index=True)
    print(f"Saved CSV as {datetime.now()}.csv")
    return {
        'statusCode': 200,
        'body': f"Data from the last 24 hours stored to S3 as CSV"
    }

lambda_handler(None, None)