# 💡 Project: Data Engineering - Batch Processing Pipeline

# Course: DLMDSEDE02 - Data Engineering (IU International University)
## Task 1 - Build a batch-processing-based data architecture
## Phase 2 - Development & Reflection

### 📈 Overview

This project implements the batch-processing data architecture conceptualized in Phase 1. It demonstrates a complete pipeline for ingesting, processing, and storing household energy consumption data using modern data engineering tools and practices. The system reads raw data, cleans it, aggregates energy consumption quarterly, and stores the results in a PostgreSQL database, ready for potential downstream machine learning applications.

---

### 🏗️ Architecture & Microservices

The system follows a microservices architecture, orchestrated locally via Docker Compose to ensure Infrastructure as Code (IaC) principles for reproducibility.

The core components running in isolated containers are:

- 📨 Kafka (confluentinc/cp-kafka:7.5.0): Handles reliable, fault-tolerant data ingestion. Raw records are published to the raw_energy topic.

- 🔗 Zookeeper (confluentinc/cp-zookeeper:latest): Manages Kafka cluster state (required dependency).

- 💾 HDFS (bde2020/hadoop-namenode:2.0.0-hadoop3.1.1-java8): Represents the conceptual distributed raw data storage layer. (Note: Data is read directly from Kafka in this specific processing script).

- ✨ Spark (apache/spark:3.5.1): Executes the core batch processing logic. Reads from Kafka, performs transformations (cleaning, type casting, date parsing), aggregates data quarterly, and writes results.

- 📊 PostgreSQL (postgres:latest): Serves as the data delivery layer, storing the final aggregated quarterly results (quarterly_energy_data table).

---

### 🛠️ Technologies Used

- Orchestration: Docker & Docker Compose

- Ingestion: Apache Kafka

- Processing: Apache Spark (using PySpark API)

- Storage (Conceptual): HDFS

- Storage (Final Aggregates): PostgreSQL

- Languages: Python 3.8+ (for Spark scripts)

- Key Python Libraries: pyspark, pandas (for ingestion), kafka-python (for ingestion)

---

### Version Control: Git & GitHub

---

### ⚙️ Core Workflow

#### Data Ingestion:

- The ingest_to_kafka.py script reads the raw .txt data using pandas.

- Each row is converted to JSON format.

- Messages are published to the raw_energy Kafka topic.

#### Batch Processing:

The process_with_spark.py script reads the JSON messages from Kafka using Spark Structured Streaming's batch mode (read).

#### Data Cleaning & Transformation:

- Spark parses the JSON payload.

- Data types are cast appropriately (e.g., numerics, timestamps).

- Missing values (?) are handled (filtered out in this implementation).

- Timestamp information is used to derive the calendar quarter.

#### Quarterly Aggregation:

- The cleaned data is grouped by the derived quarter.

- The total energy consumption (Global_active_power converted to Watt-hours) and the count of records are calculated for each quarter.

#### Data Loading:

The final aggregated Spark DataFrame is written via JDBC to the quarterly_energy_data table in PostgreSQL.

---

## 🚀 How to Run the Project

Follow these steps precisely in your terminal from the project's root directory:

- **Clone the Repository:**

    git clone [https://github.com/Nikita-DS02/Data-engineering-batch-pipeline.git](https://github.com/Nikita-DS02/Data-engineering-batch-pipeline.git)
    cd Data-engineering-batch-pipeline


- **Place Data:**
 Download the dataset ("Individual household electric power consumption") from the UCI Repository. Extract it and place the household_power_consumption.txt file inside the data/ directory.

- **Build and Start Services:**
- **Launch the entire architecture using Docker Compose:**

    docker-compose up -d


    Wait ~1 minute for services to initialize. Verify all 5 containers are Up using docker ps.

- **Install Python Dependencies:**
- **Install necessary libraries within the Spark container:**

    docker exec --user root -it data-engineering-batch-pipeline-spark-1 pip install pandas kafka-python


- **Run Ingestion Script:**
    Execute the data ingestion job via spark-submit:

    docker exec --user root -it data-engineering-batch-pipeline-spark-1 /opt/spark/bin/spark-submit \
    --master 'local[*]' \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
    /opt/spark/scripts/ingest_to_kafka.py


    (Note: This step processes ~2 million records and will take several minutes).

- **Run Processing Script:**
    Execute the data processing and aggregation job via spark-submit:

    docker exec --user root -it data-engineering-batch-pipeline-spark-1 /opt/spark/bin/spark-submit \
    --master 'local[*]' \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
    --driver-class-path /opt/spark/scripts/postgresql.jar \
    --jars /opt/spark/scripts/postgresql.jar \
    /opt/spark/scripts/process_with_spark.py


- **Verify Results in PostgreSQL:**
    Connect to the database using psql:

    docker exec -it data-engineering-batch-pipeline-postgres-1 psql -U postgres -d energy_db


- **Inside the psql shell (prompt energy_db=#), query the results table:**
     ```bash
     SELECT * FROM quarterly_energy_data ORDER BY quarter;
    \q


    You should see the aggregated quarterly data.

---

### ✨ Reproducibility & Version Control

- Infrastructure as Code (IaC): The docker-compose.yml file ensures a consistent and reproducible multi-container environment setup.

- Version Control: Git is used to track all code, configuration, and documentation changes. The .gitignore file correctly excludes the large raw data file and system-specific files (.DS_Store, .zshrc), following best practices for repository management.