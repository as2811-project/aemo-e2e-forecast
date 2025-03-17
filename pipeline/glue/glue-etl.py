import datetime
from pyspark.context import SparkContext
from pyspark.sql.window import Window
from pyspark.sql.functions import lag
from awsglue.context import GlueContext
import boto3

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

bucket_name = "aemo-forecasts-bucket"
input_prefix = "landing-zone/"
output_s3_path = f"s3://{bucket_name}/curated-zone/"

seven_days_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

s3_client = boto3.client("s3")
response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=input_prefix)

file_keys = []
for obj in response.get("Contents", []):
    file_key = obj["Key"]
    filename = file_key.split("/")[-1]
    try:
        file_date = filename.split(" ")[0]
        if file_date >= seven_days_ago:
            file_keys.append(f"s3://{bucket_name}/{file_key}")
    except IndexError:
        continue


df = spark.read.option("header", "true").csv(file_keys)
df = df.select("SETTLEMENTDATE", "RRP", "TOTALDEMAND")

window_spec = Window.orderBy("SETTLEMENTDATE")

for i in range(1, 8):
    df = df.withColumn(f"RRP_t-{i}", lag("RRP", i).over(window_spec))

df = df.dropna()
week_num = datetime.datetime.now().isocalendar()[1]
df.write.mode("overwrite").option("header", "true").csv(output_s3_path + f'training-data-week-{week_num}')

print("Processed last 4 days' files. Applied lag, and wrote data to S3.")
