from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, quarter, year, sum as spark_sum, count, date_format, expr, first
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType

# Define the schema for the incoming Kafka data (JSON format from ingest script)
schema = StructType([
    StructField("Datetime", StringType(), True), # Keep as string initially
    StructField("Global_active_power", StringType(), True),
    StructField("Global_reactive_power", StringType(), True),
    StructField("Voltage", StringType(), True),
    StructField("Global_intensity", StringType(), True),
    StructField("Sub_metering_1", StringType(), True),
    StructField("Sub_metering_2", StringType(), True),
    StructField("Sub_metering_3", StringType(), True)
])

spark = SparkSession.builder \
    .appName("EnergyQuarterlyAggregation") \
    .master("local[*]") \
    .getOrCreate()

# Disable noisy logs
spark.sparkContext.setLogLevel("WARN")

print("Reading from Kafka topic 'raw_energy'...")

# Read data from Kafka topic
# This reads ALL data available in the topic when the job runs (batch processing)
df_kafka = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "raw_energy") \
    .option("startingOffsets", "earliest") \
    .load()

print("Parsing Kafka messages...")

# Parse the JSON data from Kafka messages
df_parsed = df_kafka.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# Data Cleaning and Transformation
print("Cleaning and transforming data...")
df_transformed = df_parsed \
    .withColumn("Datetime", expr("to_timestamp(Datetime, 'yyyy-MM-dd HH:mm:ss')")) \
    .withColumn("Global_active_power_kw", col("Global_active_power").cast(DoubleType())) \
    .na.drop(subset=["Datetime", "Global_active_power_kw"]) # Drop rows with nulls

# Convert kW to Wh (assuming readings are per minute, so kW * 1000 / 60)
df_transformed = df_transformed.withColumn("Global_active_power_wh", col("Global_active_power_kw") * 1000 / 60)

# Add quarter and year columns
df_transformed = df_transformed \
    .withColumn("year", year(col("Datetime"))) \
    .withColumn("quarter_num", quarter(col("Datetime")))

# Create a proper date representing the start of the quarter
df_transformed = df_transformed.withColumn(
    "quarter_start_date",
    expr("make_date(year, (quarter_num - 1) * 3 + 1, 1)")
)

# Aggregate data by quarter
print("Aggregating data by quarter...")
aggregated = df_transformed.groupBy("quarter_start_date") \
    .agg(
        spark_sum("Global_active_power_wh").alias("total_energy_wh"),
        count("*").alias("record_count")
    ) \
    .withColumnRenamed("quarter_start_date", "quarter") \
    .orderBy("quarter") # Order results for clarity


# --- PostgreSQL Connection Details ---
jdbc_url = "jdbc:postgresql://postgres:5432/energy_db"
jdbc_table = "quarterly_energy_data" # Correct table name
connection_properties = {
    "user": "postgres",
    "password": "example",
    "driver": "org.postgresql.Driver"
}

print(f"Writing aggregated data to PostgreSQL table '{jdbc_table}'...")

# Write the aggregated data to PostgreSQL
aggregated.write \
    .jdbc(url=jdbc_url, table=jdbc_table, mode="overwrite", properties=connection_properties)

print("Data successfully written to PostgreSQL.")

spark.stop()
print("Spark session stopped.")