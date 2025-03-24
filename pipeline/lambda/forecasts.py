from decimal import Decimal
import boto3
import pandas as pd
import pickle
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

bucket_name = os.getenv('S3_BUCKET')
dynamodb_table = os.getenv('DDB_TABLE')

def clear_dynamodb_table(table):
    try:
        print("Clearing DynamoDB table...")
        response = table.scan(ProjectionExpression='SETTLEMENTDATE')
        items = response.get('Items', [])

        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'SETTLEMENTDATE': item['SETTLEMENTDATE']})
        print("DynamoDB table cleared successfully.")
    except Exception as e:
        print(f"Error clearing DynamoDB table: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    AWS Lambda function to fetch the latest 7 days of data from S3,
    generate time series forecasts using an XGBoost model,
    and store the results in DynamoDB.

    Steps:
    1. Load the XGBoost model from S3.
    2. Fetch the last 7 days of data from S3.
    3. Generate time-based features and lagged values.
    4. Use the model to predict the next 48 time steps.
    5. Store both actuals and forecasts in DynamoDB.

    Error Handling:
    - Logs errors and raises exceptions if data/model loading fails.
    - Ensures missing or malformed data is handled gracefully.
    """
    try:
        print("Starting Lambda execution")

        # Load environment variables
        if not bucket_name or not dynamodb_table:
            raise ValueError("Environment variables have not been set")

        model_key = 'models/xgboost_model.pkl'
        data_prefix = 'landing-zone/'


        s3 = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(dynamodb_table)

        clear_dynamodb_table(table)

        print("Downloading model from S3...")
        local_model_path = '/tmp/model.pkl'
        s3.download_file(bucket_name, model_key, local_model_path)
        with open(local_model_path, 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully.")

        print("Fetching data from S3...")
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=data_prefix)
        if 'Contents' not in response:
            raise Exception("No files found in landing-zone.")

        sorted_files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        latest_files = [f['Key'] for f in sorted_files][:3]
        print("Latest files: {}".format(latest_files))

        df_list = []
        for file_key in latest_files:
            local_path = f'/tmp/{os.path.basename(file_key)}'
            s3.download_file(bucket_name, file_key, local_path)
            df_list.append(pd.read_csv(local_path))

        df = pd.concat(df_list).drop_duplicates().reset_index(drop=True)
        df['SETTLEMENTDATE'] = pd.to_datetime(df['SETTLEMENTDATE'], errors='coerce')
        df = df[5::6]
        df = df.dropna(subset=['SETTLEMENTDATE'])
        df = df.sort_values(by='SETTLEMENTDATE')

        print("Data loaded and preprocessed.")

        last_timestamp = df['SETTLEMENTDATE'].max()
        future_dates = [last_timestamp + timedelta(minutes=30 * i) for i in range(1, 49)]
        future_df = pd.DataFrame({'SETTLEMENTDATE': future_dates})

        # Combine actuals and future dates
        combined = pd.concat([df, future_df], ignore_index=True)
        combined['hour'] = combined['SETTLEMENTDATE'].dt.hour
        combined['dayofweek'] = combined['SETTLEMENTDATE'].dt.dayofweek
        combined['month'] = combined['SETTLEMENTDATE'].dt.month
        combined['dayofyear'] = combined['SETTLEMENTDATE'].dt.dayofyear

        target_map = combined.set_index('SETTLEMENTDATE')['RRP'].to_dict()
        combined['rrp_lag1'] = combined['SETTLEMENTDATE'].apply(
            lambda x: target_map.get(x - pd.Timedelta('1 day'))
        )
        combined = combined.sort_index()
        combined = combined.iloc[-49:]


        features = ['rrp_lag1', 'hour', 'dayofweek', 'month', 'dayofyear']
        X_input = combined[features].values
        predictions = model.predict(X_input)
        print("Predictions generated successfully.")

        results = []
        # Store forecast results
        for i, date in enumerate(future_dates):
            results.append(
                {'SETTLEMENTDATE': date.isoformat(), 'RRP': Decimal(str(predictions[i + 1])), 'PeriodType': 'Forecast'})

        last_day = df.iloc[-48:][['SETTLEMENTDATE', 'RRP']]
        for _, row in last_day.iterrows():
            if pd.notna(row['RRP']):
                results.append({'SETTLEMENTDATE': row['SETTLEMENTDATE'].isoformat(), 'RRP': Decimal(str(row['RRP'])),
                                'PeriodType': 'Actual'})

        with table.batch_writer() as batch:
            for item in results:
                batch.put_item(Item=item)
        print("New forecasts stored in DynamoDB successfully.")

        return {'statusCode': 200, 'body': json.dumps('DynamoDB wiped and new forecasts stored successfully')}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}