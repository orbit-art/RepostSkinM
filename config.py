import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    bot_token: str
    channel_id: int
    main_admin_id: int
    db_path: str


def load_config() -> Settings:
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        channel_id=int(os.getenv("CHANNEL_ID", "0")),
        main_admin_id=int(os.getenv("MAIN_ADMIN_ID", "0")),
        db_path=os.getenv("DB_PATH", "bot.db"),
    )
