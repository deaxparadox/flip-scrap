import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

def print_message(message):
    print("-"*100)
    print(message)
    print("\n")

DATABASE_URL = "{DB}+{DBDRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}".format(
    DB = "postgresql",
    DBDRIVER = os.environ.get("DATABASE_DRIVER"),
    DBNAME = os.environ.get("DBNAME"),
    USERNAME = os.environ.get("USERNAME"),
    PASSWORD = os.environ.get("PASSWORD"),
    HOST = os.environ.get("HOST"),
    PORT = os.environ.get("PORT")
)

# print_message(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)


def get_session():
    db = Session()
    try:
        return db
    finally:
        db.close()