import pandas as pd
from kafka import KafkaProducer
import json
import time

# Load data
df = pd.read_csv('/opt/spark/data/household_power_consumption.txt', sep=';', parse_dates={'Datetime': ['Date', 'Time']}, date_format='%d/%m/%Y %H:%M:%S', na_values=['?'])
print(f"Loaded {len(df)} rows from household_power_consumption.txt")

# Convert Timestamp to string
df['Datetime'] = df['Datetime'].astype(str)
print("Converted Datetime to string")

# Initialize Kafka producer
producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
print("Kafka producer initialized")

# Send data to Kafka
start_time = time.time()
for i, (_, row) in enumerate(df.iterrows()):
    record = row.to_dict()
    producer.send('raw_energy', record)
    if i % 1000 == 0:  # Log every 1000 records
        print(f"Sent {i} records, elapsed time: {time.time() - start_time:.2f} seconds")

# Flush to ensure all messages are sent
producer.flush()
print("Flushed all messages to Kafka")
producer.close()
print("Producer closed, ingestion complete")