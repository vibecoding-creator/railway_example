from sqlmodel import SQLModel, create_engine, Field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL handling
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)


class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reserver_name: str
    room_name: str
    start_time: int  # 9 to 18
    end_time: int  # 10 to 19


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
