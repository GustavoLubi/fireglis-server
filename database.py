from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine(
    "sqlite:///fireglis.db",
    connect_args={
        "check_same_thread": False
    }
)


Session = sessionmaker(
    bind=engine
)


Base = declarative_base()