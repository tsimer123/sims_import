import psycopg2 as pg
import pandas as pd
from sqlalchemy import create_engine

conn_string = "postgresql://postgres:1234@localhost:5432/bot_adpu"

db = create_engine(conn_string)
conn = db.connect()
df = pd.read_sql("select * from sims", con=conn)
conn.close()
df.to_excel("output.xlsx", index=False)
