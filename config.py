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
os.makedirs(CAR_PHOTO_PATH, exist_ok=True)
