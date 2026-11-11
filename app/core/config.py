from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Secure RAG Chatbot"
    app_env: str = "development"
    debug: bool = True

    demo_ali_password: str
    demo_sara_password: str
    demo_admin_password: str

    database_url: str

    secret_key: str
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()