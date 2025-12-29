import json
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    # DATABASE_SQLITE = 'sqlite+aiosqlite:///data/db.sqlite3'
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def get_db_url(self):
        return (f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

        
settings = Settings()

# Users
class AdminsSettings:
    MAIN_ADMIN_ID = [1005462960]
    ADMIN_ID = [1005462960]

    @classmethod
    def load_admins(cls):
        try:
            with open("admins.json", 'r') as admin_file:
                data = json.load(admin_file)

                cls.MAIN_ADMIN_ID = data.get('main_admin', [])
                cls.ADMIN_ID = data.get('admins', [])

        except FileNotFoundError:
            pass

    @classmethod
    def save_admins(cls):
        with open('admins.json', 'w') as admin_file:
            json.dump(
                {
                    'main_admin': cls.MAIN_ADMIN_ID,
                    'admins': cls.ADMIN_ID
                },
                admin_file
            )

    @classmethod
    def add_admin(cls, user_id):
        if not user_id in cls.ADMIN_ID:
            cls.ADMIN_ID.append(user_id)

    @classmethod
    def remove_admin(cls, user_id):
        if user_id in cls.ADMIN_ID:
            cls.ADMIN_ID.remove(user_id)

# Save paths

DOWNLOAD_DIR = Path("user_data")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

PASSPORTS_PHOTO_PATH = DOWNLOAD_DIR / "passports"
os.makedirs(PASSPORTS_PHOTO_PATH, exist_ok=True)

DRIVE_LICENSES_PATH = DOWNLOAD_DIR / "drive_licenses"
os.makedirs(DRIVE_LICENSES_PATH, exist_ok=True)

CAR_PHOTO_PATH = DOWNLOAD_DIR / "cars"
os.makedirs(CAR_PHOTO_PATH, exist_ok=True)

CAR_VIDEO_PATH = DOWNLOAD_DIR / "car_video"
os.makedirs(CAR_VIDEO_PATH, exist_ok=True)

# texts

class RulesData:
    rules = "Правила"

try:
    with open("rules.txt", 'r', encoding='utf-8') as file:
        RulesData.rules = file.read()

except FileNotFoundError:
    pass
