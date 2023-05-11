from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    mongo_initdb_database: str

    class Config:
        env_file = "../.env"
        


settings = Settings()

