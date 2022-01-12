from mongoengine import connect
from settings import get_settings

# Connect to MongoDB
connect(host=get_settings().mongodb_conn_str)
