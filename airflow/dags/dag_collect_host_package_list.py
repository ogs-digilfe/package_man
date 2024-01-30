from pathlib import Path
import sys

# set package_man project root directory in string type object
CURRENT_DIR = Path(__file__).parent
PJROOT_DIR = CURRENT_DIR.parent.parent
AIRFLOW_ROOT_DIR = PJROOT_DIR / "airflow" 

sys.path.append(str(AIRFLOW_ROOT_DIR))

import lib_package_man
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5)
}

# 読み込まれたタイミングを、start_dateを設定する
# sdt = datetime.now()
# catchup = falseを設定しないと、過去に実行できなかったものをすべて実行しなおしてしまう。(defaultはTrue)
with DAG(
    dag_id="collect_host_package_list_v0.6",
    default_args=default_args,
    description="Collect and Update host packages installed",
    start_date=datetime(2024, 1, 24, 16),
    schedule="0 2 * * *",
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id = "update_playbooks",
        python_callable = lib_package_man.update_playbook,
    )

    task2 = PythonOperator(
        task_id = "collect_and_update_installed_host_packages",
        python_callable = lib_package_man.collect_and_update_data,
    )

    task3 = PythonOperator(
        task_id = "update_host_packages_parquet_data",
        python_callable = lib_package_man.update_parquet_data,
    )

    task4 = PythonOperator(
        task_id = "backup_settings_package_man_files",
        python_callable = lib_package_man.backup_settings_package_man_files,
    )

    task1 >> task2
    task2 >> task3
    task3 >> task4