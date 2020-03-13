# Airflow

Sample Apache Airflow project.
# Setup:
Clone repo
```
$ pip install virtualenv
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ export AIRFLOW_HOME=~/Airflow/
$ airflow initdb
```
Current DAGS and function:
1. bollinger_bands:
* Pulls current S&P 500 data using API call and calculates the Bollinger Bands.  Sends notifcation email if buying or selling opportunity recognized. Second task creates a plot.

2. tutorial:
* Example project with BashOperator 
