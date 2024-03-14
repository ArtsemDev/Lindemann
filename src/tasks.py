from asyncio import sleep
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot.keyboards.inline.task import task_detail_ikb
from src.models import Task
from src.settings import broker, async_session_maker, bot


@broker.task(schedule=[{"cron": "*/15 * * * *"}])
async def pending_tasks():
    async with async_session_maker() as session:  # type: AsyncSession
        now = datetime.now().replace(tzinfo=None)
        tasks = await session.scalars(
            statement=select(Task).options(joinedload(Task.user))
            .filter(Task.is_done == False)
            .filter(Task.end_date.between(now, now + timedelta(minutes=15)))
        )
        tasks = tasks.unique().all()
        for task in tasks:
            await bot.send_message(
                chat_id=task.user.id,
                text=f"<b>Задача подходит к концу:</b>\n\n{task.info}",
                reply_markup=task_detail_ikb(task=task)
            )
            await sleep(0.5)
