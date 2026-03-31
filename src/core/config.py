from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    PROJECT_NAME: str = "Quantum LLM API"
    MODEL_PATH: str = "./models/opt-125m"

    class Config:
        env_file = ".env"


settings = Settings()