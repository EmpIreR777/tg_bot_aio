import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_ROOT_PASSWORD: str

    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    )

    def get_bot_token(self):
        return self.BOT_TOKEN

    def get_id_admin(self):
        return self.ADMIN_ID

    def get_db_root_password(self):
        return self.POSTGRES_ROOT_PASSWORD

    def get_db_url(self):
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
            f'{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )
    # PG_URL=postgresql://postgres_user_aio:postgres_password_aio@localhost:5430/postgres_db_aio

    def get_redis_url(self):
        return (f'redis://:{self.REDIS_PASSWORD}@'
                f'{self.REDIS_HOST}:{self.REDIS_PORT}/0')
    # REDIS_URL=redis://:your_secure_password@127.0.0.1:6380/0

setting = Settings()
