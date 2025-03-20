import boto3
import pandas as pd
import numpy as np
import pickle
import json
import os
from datetime import datetime, timedelta


def clear_dynamodb_table(table):
    response = table.scan(ProjectionExpression='DateTime')  # Get all DateTime keys
    items = response.get('Items', [])

    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={'DateTime': item['DateTime']})

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
        bucket_name = os.environ['S3_BUCKET']
        model_key = 'models/xgb_reg.pkl'
        data_prefix = 'landing-zone/'
        dynamodb_table = os.environ.get('DDB_TABLE')

        s3 = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(dynamodb_table)
        clear_dynamodb_table(table)

        # Load model from S3
        local_model_path = '/tmp/model.pkl'
        s3.download_file(bucket_name, model_key, local_model_path)
        with open(local_model_path, 'rb') as f:
            model = pickle.load(f)

        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=data_prefix)
        if 'Contents' not in response:
            raise Exception("No files found in landing-zone.")

        sorted_files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        latest_files = [f['Key'] for f in sorted_files][:7]

        df_list = []
        for file_key in latest_files:
            local_path = f'/tmp/{os.path.basename(file_key)}'
            s3.download_file(bucket_name, file_key, local_path)
            df_list.append(pd.read_csv(local_path))

        df = pd.concat(df_list).drop_duplicates().reset_index(drop=True)
        df['SETTLEMENTDATE'] = pd.to_datetime(df['SETTLEMENTDATE'], errors='coerce')
        df = df.dropna(subset=['SETTLEMENTDATE'])

        # Generate features
        df['hour'] = df['SETTLEMENTDATE'].dt.hour
        df['dayofweek'] = df['SETTLEMENTDATE'].dt.dayofweek
        df['month'] = df['SETTLEMENTDATE'].dt.month
        df['dayofyear'] = df['SETTLEMENTDATE'].dt.dayofyear

        target_map = df.set_index('SETTLEMENTDATE')['RRP'].to_dict()
        df['rrp_lag1'] = df['SETTLEMENTDATE'].apply(
            lambda x: target_map.get(x - pd.Timedelta('1 day'), np.nan)
        )

        last_timestamp = df['SETTLEMENTDATE'].max()
        future_dates = [last_timestamp + timedelta(minutes=30 * i) for i in range(1, 49)]
        future_df = pd.DataFrame({'SETTLEMENTDATE': future_dates})

        combined = pd.concat([df, future_df], ignore_index=True)
        combined = combined.iloc[-49:]

        features = ['rrp_lag1', 'hour', 'dayofweek', 'month', 'dayofyear']
        X_input = combined[features].values

        # Generate predictions
        predictions = model.predict(X_input)

        results = []
        expiry_time = int((datetime.utcnow() + timedelta(days=1)).timestamp())

        # Forecasts
        for i, date in enumerate(future_dates):
            results.append({'SETTLEMENTDATE': date.isoformat(), 'RRP': float(predictions[i + 1]), 'PeriodType': 'Forecast', 'TimeToExist': expiry_time})

        last_day = df.iloc[-48:][['SETTLEMENTDATE', 'RRP']]

        # Actuals
        for _, row in last_day.iterrows():
            if pd.notna(row['RRP']):  # Avoid NaN values
                results.append(
                    {'SETTLEMENTDATE': row['SETTLEMENTDATE'].isoformat(), 'RRP': float(row['RRP']), 'PeriodType': 'Actual', 'TimeToExist': expiry_time})

        # Batch write to DynamoDB
        with table.batch_writer() as batch:
            for item in results:
                batch.put_item(Item=item)

        return {'statusCode': 200, 'body': json.dumps('Forecasts stored successfully')}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}
