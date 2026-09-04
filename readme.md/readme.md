# 🏏 Cricket Analytics Data Engineering Project

An end-to-end cricket analytics project built using Snowflake, dbt,
Apache Airflow, Docker, Python, SQL, and Streamlit.

The project demonstrates a modern data engineering pipeline that
transforms raw cricket data into analytics-ready datasets and
visualizes the results through an interactive dashboard.

---

## 🏗️ Architecture

```text
Raw Cricket CSV Data
        │
        ▼
    Snowflake
        │
        ▼
  Bronze Layer
        │
        ▼
  Silver Layer
        │
        │  dbt
        ▼
   Gold Layer
        │
        ├───────────────┐
        ▼               ▼
   Streamlit        Analytics
   Dashboard          Tables

Apache Airflow
      │
      ▼
Orchestrates dbt
Debug → Run → Test
Cricket CSV Files
       ↓
Snowflake
       ↓
Bronze
       ↓
Silver
       ↓
dbt
       ↓
Gold
       ↓
Streamlit