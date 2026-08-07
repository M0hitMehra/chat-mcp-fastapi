from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    MONGO_URI = os.getenv("MONGO_URI")

    DATABASE_NAME = os.getenv("DATABASE_NAME")

    JWT_SECRET = os.getenv("JWT_SECRET")

    APP_NAME: str = os.getenv("APP_NAME")

    APP_VERSION: str = os.getenv("APP_VERSION")

    DEBUG: bool = os.getenv("DEBUG")


settings = Settings()
