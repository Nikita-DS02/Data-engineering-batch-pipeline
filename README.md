💡 Project: Data Engineering - Batch Processing Pipeline (DLMDSEDE02 - Task 1)

This project implements a batch-processing data architecture for analyzing household energy consumption data. It fulfills the requirements for Phase 2 (Development/Reflection) of the IU International University of Applied Sciences Data Engineering course portfolio (DLMDSEDE02).

🏛️ Architecture Overview

The system utilizes a microservices architecture, orchestrated locally using Docker Compose. This aligns with the concepts developed in Phase 1 and processes data in scheduled batches.

The core components are:

📨 Kafka (confluentinc/cp-kafka:7.5.0): Handles reliable data ingestion. Raw household power consumption data is published to the raw_energy topic.

💾 HDFS (bde2020/hadoop-namenode:2.0.0-hadoop3.1.1-java8): Serves as the conceptual distributed storage layer for raw data. (Note: In this specific implementation, Spark reads directly from Kafka).

✨ Spark (apache/spark:3.5.1): Performs the core batch processing. It reads JSON data from the Kafka topic, parses/cleans records, aggregates energy consumption quarterly, and writes the final results.

📊 PostgreSQL (postgres:latest): Acts as the data serving layer, storing the final aggregated quarterly results in the quarterly_energy_data table for potential downstream ML applications.

🔗 Zookeeper (confluentinc/cp-zookeeper:latest): Manages Kafka cluster state (required dependency).

📋 Requirements

To run this project, you will need:

🐳 Docker & Docker Compose: For running the containerized services.

🐙 Git: For version control and cloning the repository.

📄 Dataset: The "Individual household electric power consumption Data Set" from the UCI Machine Learning Repository. Download the .zip file, extract it, and place the household_power_consumption.txt file in the data/ directory of this project.

🚀 How to Run the Pipeline

Follow these steps precisely to set up the environment and execute the data pipeline:

Clone the Repository:

git clone [https://github.com/Nikita-DS02/Data-engineering-batch-pipeline.git](https://github.com/Nikita-DS02/Data-engineering-batch-pipeline.git)
cd Data-engineering-batch-pipeline


Place Data:
Ensure the household_power_consumption.txt dataset file is located inside the data/ directory within the cloned project folder.

Build and Start Services:
From the project root directory, launch all services using Docker Compose:

docker-compose up -d


Wait about a minute for all containers (Kafka, Zookeeper, HDFS, Postgres, Spark) to initialize. Verify they are running using docker ps.

Install Python Dependencies:
Install the required Python libraries (pandas, kafka-python) inside the running Spark container:

docker exec --user root -it data-engineering-batch-pipeline-spark-1 pip install pandas kafka-python


Run Ingestion Script:
Submit the Python script (ingest_to_kafka.py) using spark-submit. This reads the raw .txt file and publishes each record as a JSON message to the Kafka raw_energy topic:

docker exec --user root -it data-engineering-batch-pipeline-spark-1 /opt/spark/bin/spark-submit \
  --master 'local[*]' \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /opt/spark/scripts/ingest_to_kafka.py


(Note: This step processes ~2 million records and will take several minutes to complete).

Run Processing Script:
Submit the main Spark processing script (process_with_spark.py). This reads the JSON messages from Kafka, performs cleaning, aggregates data quarterly, and writes the final results to PostgreSQL:

docker exec --user root -it data-engineering-batch-pipeline-spark-1 /opt/spark/bin/spark-submit \
  --master 'local[*]' \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  --driver-class-path /opt/spark/scripts/postgresql.jar \
  --jars /opt/spark/scripts/postgresql.jar \
  /opt/spark/scripts/process_with_spark.py


Verify Results in PostgreSQL:
Connect to the PostgreSQL container using psql and query the final table:

docker exec -it data-engineering-batch-pipeline-postgres-1 psql -U postgres -d energy_db


Inside the psql shell (prompt energy_db=#), run:

SELECT * FROM quarterly_energy_data ORDER BY quarter;
\q


You should see the aggregated data listed per quarter.

✨ Reproducibility

This project emphasizes reproducibility, a key data engineering principle:

Infrastructure as Code (IaC): The docker-compose.yml file defines the entire multi-container environment, ensuring consistent setup across different machines.

Version Control: All source code, configuration files, and documentation are tracked using Git, enabling collaboration and history tracking.