from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="cricket_dbt_pipeline",
    start_date=datetime(2026, 9, 4),
    schedule="@daily",
    catchup=False,
) as dag:

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=(
            "dbt debug "
            "--project-dir /opt/airflow/dbt_project "
            "--profiles-dir /opt/airflow/dbt_profiles"
        ),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "dbt run "
            "--no-partial-parse "
            "--project-dir /opt/airflow/dbt_project "
            "--profiles-dir /opt/airflow/dbt_profiles"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
           "dbt test "
           "--no-partial-parse "
           "--project-dir /opt/airflow/dbt_project "
           "--profiles-dir /opt/airflow/dbt_profiles"
        ),
    )

    dbt_debug >> dbt_run >> dbt_test