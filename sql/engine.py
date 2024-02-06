import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy import URL

load_dotenv()

username_db = os.getenv('username_db')
password_db = os.getenv('password_db')
host_db = os.getenv('host_db')
port_db = os.getenv('port_db')
database = os.getenv('database')

url_object = URL.create(
    "postgresql+psycopg2",
    username=username_db,
    password=password_db,
    host=host_db,
    port=port_db,
    database=database,
)

engine = create_engine(url_object)
# engine = create_engine(url_object, echo=True)