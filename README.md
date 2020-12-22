# Airflow

Sample Apache Airflow project.
# Setup:
Clone repo
```
$ sudo apt-get install libatlas-base-dev
$ sudo apt-get install python3-venv
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ export AIRFLOW_HOME=~/Airflow/
$ airflow initdb
```
Update airflow.cfg smtp settings:
```
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = <my email>@gmail.com
smtp_password = <get this from Google>
smtp_port = 587
smtp_mail_from = <my email>@gmail.com
```

Current DAGS and function:
1. bollinger_bands:
* Pulls current S&P 500 data using API call and calculates the Bollinger Bands.  Sends notifcation email if buying or selling opportunity recognized. Second task creates a plot.

2. tutorial:
* Example project with BashOperator 

