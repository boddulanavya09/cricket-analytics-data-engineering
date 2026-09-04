# 🏏 Cricket Analytics Data Engineering Project

An end-to-end cricket analytics data engineering project built using Snowflake, dbt, Apache Airflow, Docker, and Streamlit.

## 📌 Project Overview

This project demonstrates how raw cricket data can be transformed into analytics-ready datasets and visualized through an interactive dashboard.

The pipeline follows a modern data engineering architecture:

Raw CSV Data → Snowflake → dbt → Gold Analytics → Streamlit

Apache Airflow is used to orchestrate the dbt pipeline.

## 🏗️ Architecture

```text
Cricket CSV Data
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