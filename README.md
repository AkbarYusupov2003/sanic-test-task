# <a href="https://docs.google.com/document/d/1lblqae9k0wdV7q7QFjxYcC_rrDbRb5DIUHtHiKM5iz4/edit">sanic-test-task</a>
# How to launch the project
```
  pip install -r requirements.txt
  sudo -u postgres createdb DimaTech
  sudo service redis-server start
```
# How to create an admin user
```
  python commands.py create_admin username password
```
# Notes:
### The "/swagger" endpoint is fully documented
### The "payment/webhook" endpoint uses sql transaction statement
