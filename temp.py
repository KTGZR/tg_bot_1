#1
from dataclasses import dataclass
from typing import List
@dataclass(frozen=True)
class TelegramBot:
    token: str
    adm_ids: List[int]

@dataclass 
class DataBaseConnection:
    db_host: str
    db_user: str
    db_password: str
    database: str

@dataclass 
class Config:
    tg_bot: TelegramBot
    db: DataBaseConnection