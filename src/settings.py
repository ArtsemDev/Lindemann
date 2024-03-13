from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, RedisEventIsolation
from pydantic import SecretStr, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from taskiq import TaskiqScheduler, InMemoryBroker
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    FSM_STORAGE_URL: RedisDsn
    DATABASE_URL: PostgresDsn
    TASK_BROKER_STORAGE: RedisDsn


settings = Settings()
async_engine = create_async_engine(url=settings.DATABASE_URL.unicode_string())
async_session_maker = async_sessionmaker(bind=async_engine)
bot = Bot(
    token=settings.BOT_TOKEN.get_secret_value(),
    parse_mode=ParseMode.HTML
)
fsm_storage = RedisStorage.from_url(url=settings.FSM_STORAGE_URL.unicode_string())
events_isolation = RedisEventIsolation(redis=fsm_storage.redis)
dp = Dispatcher(
    storage=fsm_storage,
    events_isolation=events_isolation
)
broker = ListQueueBroker(url=settings.TASK_BROKER_STORAGE.unicode_string())
scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker=broker)])
