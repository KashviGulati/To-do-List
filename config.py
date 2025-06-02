import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")  
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///todo.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
