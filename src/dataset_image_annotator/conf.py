from pydantic import PostgresDsn, SecretStr
from python3_commons.conf import CommonSettings


class Settings(CommonSettings):
    db_dsn: PostgresDsn = None
    service_addr: str = '127.0.0.1'
    service_port: int = 8080
    bootstrap_user_email: str | None = None
    bootstrap_user_password: SecretStr = None
    auth_secret: SecretStr = 'TODO-REPLACE'
    timezone: str = 'UTC'


settings = Settings()
