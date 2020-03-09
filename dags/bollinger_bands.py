import sys
import os
sys.path.append(os.path.join( os.path.dirname(__file__), os.path.pardir))
from bollinger import calc_bb
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('bollinger', default_args=default_args, schedule_interval=None)

t1 = PythonOperator(
    task_id='bb',
    python_callable=calc_bb.get_spy_data,
    #schedule_interval="0 13 * * *",
    provide_context=True,
    dag=dag,
)

t2 = PythonOperator(
    task_id='plot_bb',
    python_callable=calc_bb.plot,
    dag=dag,
)

t1.set_downstream(t2)



