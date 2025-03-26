import os
from dotenv import load_dotenv
import boto3
import pandas as pd
import numpy as np
import datetime
import pickle
import io
from decimal import Decimal
import json

load_dotenv()

S3_BUCKET = os.environ.get('S3_BUCKET')
METADATA_TABLE = os.environ.get('METADATA_TABLE')

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    model_scores_table = dynamodb.Table(METADATA_TABLE)

    current_week = datetime.datetime.now().isocalendar()[1]
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y%m%d%H%M%S")

    training_data_path = f'curated-zone/training-data-week-{current_week}'
    checkpoint_folder = 'models/checkpoints/'
    checkpoint_model = f'{checkpoint_folder}xgboost_model_{timestamp}.pkl'
    latest_model_path = 'models/xgboost_model.pkl'

    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=training_data_path
        )

        if 'Contents' not in response or not any(obj['Key'].endswith('.csv') for obj in response['Contents']):
            return {
                'statusCode': 404,
                'body': f'No CSV training data found for week {current_week}'
            }

        csv_file = next(obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.csv'))
        print(f"Loading training data from: {csv_file}")

        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=csv_file)
        training_data = pd.read_csv(io.BytesIO(obj['Body'].read()))
        training_data = training_data.set_index("SETTLEMENTDATE")

        feature_columns = ['rrp_lag1', 'hour', 'dayofweek', 'month', 'dayofyear']
        X = training_data[feature_columns]
        y = training_data['RRP']

        try:
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET,
                Prefix=checkpoint_folder
            )

            if 'Contents' in response and len(response['Contents']) > 0:
                # Sort by last modified timestamp
                checkpoints = sorted(
                    response['Contents'],
                    key=lambda x: x['LastModified'],
                    reverse=True
                )

                latest_checkpoint = checkpoints[0]['Key']
                print(f"Found latest checkpoint: {latest_checkpoint}")

                obj = s3_client.get_object(Bucket=S3_BUCKET, Key=latest_checkpoint)
                model = pickle.loads(obj['Body'].read())
                print(f"Loaded existing model as checkpoint: {latest_checkpoint}")

                model.fit(X, y, xgb_model=model)
            else:
                print("No checkpoint models found")
        except Exception as e:
            print(f"Error finding or loading checkpoint model: {str(e)}")


        model_bytes = pickle.dumps(model)

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=checkpoint_model,
            Body=model_bytes
        )

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=latest_model_path,
            Body=model_bytes
        )

        predictions = model.predict(X)
        mse = np.mean((predictions - y) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - y))
        r2 = 1 - (np.sum((y - predictions) ** 2) / np.sum((y - np.mean(y)) ** 2))

        try:
            version_count = model_scores_table.scan(
                Select='COUNT'
            )['Count']
            new_version = version_count + 1
        except Exception as e:
            print(f"Error getting version count: {str(e)}")
            new_version = 1

        model_entry = {
            'model_id': f"model_v{new_version}",
            'version': new_version,
            'model_path': checkpoint_model,
            'training_date': current_time.isoformat(),
            'training_week': current_week,
            'training_samples': len(training_data),
            'rmse': Decimal(str(round(rmse, 6))),
            'mae': Decimal(str(round(mae, 6))),
            'r2': Decimal(str(round(r2, 6))),
            'mse': Decimal(str(round(mse, 6))),
            'feature_columns': json.dumps(feature_columns)
        }

        model_scores_table.put_item(Item=model_entry)

        return {
            'statusCode': 200,
            'body': f'Model v{new_version} successfully trained and saved.',
            'metrics': {
                'version': new_version,
                'rmse': float(rmse),
                'mae': float(mae),
                'r2': float(r2),
                'training_samples': len(training_data),
                'model_path': checkpoint_model
            }
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error training model: {str(e)}'
        }