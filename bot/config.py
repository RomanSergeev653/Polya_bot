from functools import cached_property
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "shop.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    admin_user_ids: str

    @field_validator("admin_user_ids", mode="after")
    @classmethod
    def _validate_admin_ids(cls, value: str) -> str:
        parts = [p.strip() for p in value.split(",") if p.strip()]
        if not parts:
            raise ValueError("ADMIN_USER_IDS must contain at least one id")
        for p in parts:
            if not p.isdigit():
                raise ValueError(f"ADMIN_USER_IDS contains non-numeric value: {p!r}")
        return ",".join(parts)

    @cached_property
    def admin_ids(self) -> list[int]:
        return [int(p) for p in self.admin_user_ids.split(",") if p.strip()]

    @property
    def primary_admin_id(self) -> int:
        return self.admin_ids[0]

    def is_admin(self, user_id: int | None) -> bool:
        return user_id is not None and user_id in self.admin_ids


settings = Settings()
