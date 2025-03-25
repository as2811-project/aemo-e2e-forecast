import datetime
from pyspark.context import SparkContext
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, col, hour, dayofweek, month, dayofyear
from pyspark.sql.functions import monotonically_increasing_id, expr, to_timestamp
from awsglue.context import GlueContext
import boto3

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

bucket_name = "as-aemo-forecasts"
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
        file_date = filename.split("_")[1].split(".")[0]
        if file_date >= seven_days_ago:
            file_keys.append(f"s3://{bucket_name}/{file_key}")
    except IndexError:
        continue

df = spark.read.option("header", "true").csv(file_keys)
df = df.withColumn("SETTLEMENTDATE", to_timestamp(col("SETTLEMENTDATE")))

df = df.select(
    "SETTLEMENTDATE",
    "RRP",
    hour(col("SETTLEMENTDATE")).alias("hour"),
    dayofweek(col("SETTLEMENTDATE")).alias("dayofweek"),
    month(col("SETTLEMENTDATE")).alias("month"),
    dayofyear(col("SETTLEMENTDATE")).alias("dayofyear")
)

window_spec = Window.orderBy("SETTLEMENTDATE")

# Apply lag and other processing steps
df = df.withColumn("rrp_lag1", lag("RRP", 48).over(window_spec))
df = df.dropna()
df_with_index = df.withColumn("row_id", monotonically_increasing_id())
filtered_df = df_with_index.filter(expr("(row_id - 5) % 6 = 0"))
result_df = filtered_df.drop("row_id")

week_num = datetime.datetime.now().isocalendar()[1]
result_df.write.mode("overwrite").option("header", "true").csv(output_s3_path + f'training-data-week-{week_num}')

print("Processed last 7 days' files. Added time features, applied lag, and wrote data to S3.")