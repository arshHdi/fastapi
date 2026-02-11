from database.db import Base, engine
from models.user import User
from models.activity import UserActivity
import uvicorn


class Settings:
    def __init__(self) -> None:
        self.host: str = "127.0.0.1"
        self.port: int = 8000
        self.debug: bool = True


settings = Settings()

if __name__ == "__main__":
    uvicorn.run(
        "api.crud:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )