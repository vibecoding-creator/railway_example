from sqlmodel import SQLModel, create_engine, Field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL handling
# Railway provides DATABASE_URL. For local, we can default to sqlite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Fix for some postgres drivers expecting postgresql:// instead of postgres://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
