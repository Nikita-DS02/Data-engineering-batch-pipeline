Project: Data Engineering - Batch Processing Pipeline (DLMDSEDE02 - Task 1) 
Phase 2 - Development

This project implements a batch-processing data architecture for analyzing household energy consumption data, fulfilling the requirements for Phase 2 (Development/Reflection) of the IU International University of Applied Sciences Data Engineering course portfolio (DLMDSEDE02).

🏛️ Architecture

The system utilizes a microservices architecture orchestrated locally using Docker Compose. It processes data in batches as conceptualized in Phase 1:

Kafka (confluentinc/cp-kafka:7.5.0): Handles reliable data ingestion. The raw household power consumption data is published to the raw_energy topic.

HDFS (bde2020/hadoop-namenode:2.0.0-hadoop3.1.1-java8): Serves as the conceptual distributed storage layer for raw data. Note: In this specific implementation, Spark reads directly from Kafka for simplicity.

Spark (apache/spark:3.5.1): Performs the core batch processing. It reads JSON data from the Kafka topic, parses and cleans the records, aggregates energy consumption data quarterly, and writes the final results.

PostgreSQL (postgres:latest): Acts as the data serving layer, storing the final aggregated quarterly results in the quarterly_energy_data table for potential downstream ML applications.

Zookeeper (confluentinc/cp-zookeeper:latest): Manages Kafka cluster state.

📋 Requirements

Docker & Docker Compose: For running the containerized services.

Git: For version control and cloning the repository.

Dataset: The "Individual household electric power consumption Data Set" from the UCI Machine Learning Repository (expected as household_power_consumption.txt).

🚀 How to Run

Follow these steps to set up and run the pipeline locally:

Clone the Repository:

git clone [https://github.com/Nikita-DS02/Data-engineering-batch-pipeline.git](https://github.com/Nikita-DS02/Data-engineering-batch-pipeline.git)
cd Data-engineering-batch-pipeline


Place Data:
Download the dataset and place the household_power_consumption.txt file inside the data/ directory within the cloned project folder.

Build and Start Services:
From the project root directory, run:

docker-compose up -d


Wait a minute for all containers (Kafka, Zookeeper, HDFS, Postgres, Spark) to initialize. Verify they are running using docker ps.

Install Python Dependencies:
Install required libraries (pandas for ingestion, kafka-python for the producer) inside the running Spark container:

docker exec --user root -it data-engineering-batch-pipeline-spark-1 pip install pandas kafka-python


Run Ingestion Script:
Submit the Python script (ingest_to_kafka.py) to Spark to read the raw data and publish it to the Kafka raw_energy topic:

docker exec --user root -it data-engineering-batch-pipeline-spark-1 /opt/spark/bin/spark-submit \
  --master 'local[*]' \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /opt/spark/scripts/ingest_to_kafka.py


(This step takes several minutes to process ~2 million records).

Run Processing Script:
Submit the main Spark processing script (process_with_spark.py) to read from Kafka, perform quarterly aggregation, and write to PostgreSQL:

docker exec --user root -it data-engineering-batch-pipeline-spark-1 /opt/spark/bin/spark-submit \
  --master 'local[*]' \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  --driver-class-path /opt/spark/scripts/postgresql.jar \
  --jars /opt/spark/scripts/postgresql.jar \
  /opt/spark/scripts/process_with_spark.py


Verify Results in PostgreSQL:
Connect to the PostgreSQL container and query the final table:

docker exec -it data-engineering-batch-pipeline-postgres-1 psql -U postgres -d energy_db


Inside the psql shell, run:

SELECT * FROM quarterly_energy_data ORDER BY quarter;
\q


You should see the aggregated data per quarter.

✨ Reproducibility

This project emphasizes reproducibility through:

Infrastructure as Code (IaC): docker-compose.yml defines the entire environment, ensuring consistency.

Version Control: All code and configuration are tracked using Git.