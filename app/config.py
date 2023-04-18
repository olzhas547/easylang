from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    mongo_initdb_database: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    swagger_username: str
    swagger_password: str

    class Config:
        env_file = ".env"


settings = Settings()

