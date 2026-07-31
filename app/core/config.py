from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """`.env`에서 읽어오는 앱 설정.

    database_url과 jwt_secret_key는 기본값을 두지 않는다. 소스코드에 실제 비밀번호를
    남기지 않기 위해서이고, `.env`가 없으면 앱이 조용히 잘못된 값으로 뜨는 대신
    시작 시점에 바로 에러를 내게 하려는 의도다.
    """

    app_name: str = "나의 일기(내일) API"
    app_version: str = "0.1.0"
    app_env: str = "local"

    # Database
    database_url: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # AWS S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket_name: str = ""
    aws_region: str = "ap-northeast-2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # .env에는 docker-compose 전용 변수(DB_HOST, PGADMIN_EMAIL 등)도 함께 들어 있다.
        # 여기서 선언하지 않은 값은 무시해야 앱이 뜬다.
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """설정 객체를 한 번만 만들어 재사용한다(.env 파일을 매번 다시 읽지 않도록 캐싱)."""
    return Settings()
