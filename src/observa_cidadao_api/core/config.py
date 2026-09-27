import logging
import secrets

from pydantic import PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./data/observa_cidadao.db"
    token_expira_em_minutos: PositiveInt = 60
    secret_key: str = ""
    cors_origins: list[str] = ["http://localhost:9000", "http://localhost:8080"]

    @model_validator(mode="after")
    def _gerar_chave_temporaria(self) -> "Settings":
        if not self.secret_key:
            self.secret_key = secrets.token_hex(32)
            logger.warning(
                "SECRET_KEY não definida: usando uma chave temporária. "
                "Os tokens emitidos deixam de valer quando a API reinicia."
            )
        return self


settings = Settings()
