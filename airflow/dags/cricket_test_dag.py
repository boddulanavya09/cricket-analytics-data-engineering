from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def say_hello():
    print("Hello from Cricket Analytics Airflow!")


with DAG(
    dag_id="cricket_test_dag",
    start_date=datetime(2026, 9, 4),
    schedule=None,
    catchup=False,
) as dag:

    hello_task = PythonOperator(
        task_id="hello_cricket",
        python_callable=say_hello,
    )