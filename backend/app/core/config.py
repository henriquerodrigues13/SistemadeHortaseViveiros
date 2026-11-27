"""Leitura das configurações do projeto a partir do arquivo .env."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[2] é a pasta "backend"
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Aplicação
    ambiente: Literal["desenvolvimento", "producao"] = "desenvolvimento"

    # Banco de dados
    database_url: str = "sqlite:///./data/hortas.db"

    # Segurança (sem valor padrão: se faltar no .env, a API não sobe)
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_expira_minutos: int = 60

    # Administrador Hoot (sem valor padrão)
    admin_hoot_nome: str
    admin_hoot_email: str
    admin_hoot_senha: SecretStr

    # CORS: origens separadas por vírgula
    cors_origens: str = "http://localhost:5173"

    # Valores dos requisitos
    tempo_resposta_max_segundos: int = 3
    alerta_antecedencia_dias: int = 1
    email_reenvio_intervalo_min: int = 15
    email_reenvio_max_tentativas: int = 3

    # E-mail
    email_modo: Literal["console", "smtp"] = "console"
    email_remetente: str = "hortas@exemplo.com"
    smtp_host: str = ""
    smtp_porta: int = 587
    smtp_usuario: str = ""
    smtp_senha: SecretStr = SecretStr("")

    @property
    def cors_origens_lista(self) -> list[str]:
        return [o.strip() for o in self.cors_origens.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cria as configurações uma única vez e reaproveita nas próximas chamadas."""
    return Settings()
