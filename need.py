from sqlalchemy import create_engine
from sqlalchemy import text
# or from sqlalchemy.sql import text

engine = create_engine('mysql://{USR}:{PWD}@localhost:3306/db', echo=True)

with engine.connect() as con:
    with open("database_setup.sql") as file:
        query = text(file.read())
        con.execute(query)
