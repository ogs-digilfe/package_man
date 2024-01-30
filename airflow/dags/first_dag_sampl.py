from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    "owner": "ogs-digilife",
    "retries": 5,
    "retry_delay": timedelta(minutes=2)
}

def task1_operator(d):
    print(f"hello world, this is the 1st python test task executed at {d.year}-{d.month}-{d.day} {d.hour}:{d.minute}:{d.second}")

with DAG(
    dag_id="first_python_dag_v1.31",
    default_args=default_args,
    description="This is the first python dag for test",
    start_date=datetime(2023, 11, 15, 2),
    schedule_interval="@daily"
) as dag:

    task1 = PythonOperator(
        task_id = "1st_task",
        python_callable = task1_operator,
        op_kwargs={"d": datetime.now()}
    )
