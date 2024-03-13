from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline.task import task_panel_ikb, task_detail_ikb, TaskCallbackData, approve_ikb
from bot.keyboards.reply.main import main_panel_rkb
from bot.states.task import TaskStatesGroup
from src.models import User, Task
from src.settings import async_session_maker


router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Шалом, я Бот-Список задач!",
        reply_markup=main_panel_rkb
    )
    async with async_session_maker() as session:  # type: AsyncSession
        user = User(id=message.from_user.id)
        session.add(instance=user)
        try:
            await session.commit()
        except IntegrityError:
            ...


@router.message(F.text == "СОЗДАТЬ ЗАДАЧУ 📝")
async def create_task(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(state=TaskStatesGroup.create.title)
    await message.answer(
        text="Введите название задачи\n<b>Не более 128 символов!</b>"
    )


@router.message(TaskStatesGroup.create.title)
async def get_task_title(message: Message, state: FSMContext):
    if len(message.text) > 128:
        await message.answer(
            text=f"Указанный заголовок:"
                 f"\n\n<code>{message.text}</code>"
                 f"\n\nПревышает допустимую длину в 128 символов ({len(message.text)})"
        )
    else:
        await state.update_data(title=message.text)
        await state.set_state(state=TaskStatesGroup.create.description)
        await message.answer(
            text="Введите описание задачи или введите /empty для пропуска!"
        )


@router.message(TaskStatesGroup.create.description, F.text == "/empty")
async def empty_description(message: Message, state: FSMContext):
    await state.set_state(state=TaskStatesGroup.create.end_date)
    await message.answer(
        text=f"Введите срок выполнения задачи в формате: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )


@router.message(TaskStatesGroup.create.description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await empty_description(message=message, state=state)


@router.message(TaskStatesGroup.create.end_date)
async def get_end_date(message: Message, state: FSMContext):
    try:
        end_date = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    except:
        await message.answer(
            text="Дата указанная в неверном формате, проверьте данные и повторите ввод!"
        )
    else:
        if end_date > datetime.now():
            state_data = await state.get_data()
            await state.clear()
            async with async_session_maker() as session:  # type: AsyncSession
                task = Task(**state_data, end_date=end_date)
                session.add(instance=task)
                try:
                    await session.commit()
                except IntegrityError:
                    await message.answer(
                        text="Произошла непредвиденная ошибка, повторите попытку создания задачи или обратитесь в поддержку!"
                    )
                else:
                    await message.answer(
                        text="Задача создана успешно!"
                    )
        else:
            await message.answer(
                text="Срок выполнения не может быть в прошлом!"
            )


@router.message(F.text == "МОИ ЗАДАЧИ 📋")
async def task_list(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Выберите раздел:",
        reply_markup=task_panel_ikb
    )


@router.callback_query(F.data == "task_all")
async def task_list_all(callback: CallbackQuery):
    await callback.message.delete()
    async with async_session_maker() as session:  # type: AsyncSession
        tasks = await session.scalars(
            statement=select(Task).filter(Task.user_id == callback.from_user.id)
        )
        tasks = list(tasks.all())
        if tasks:
            for task in tasks:  # type: Task
                await callback.message.answer(
                    text=task.info,
                    reply_markup=task_detail_ikb(task=task) if not task.is_done else None
                )
        else:
            await callback.message.answer(
                text="Задач не найдено!",
                reply_markup=task_panel_ikb
            )


@router.callback_query(F.data == "task_done")
async def task_done_list_all(callback: CallbackQuery):
    await callback.message.delete()
    async with async_session_maker() as session:  # type: AsyncSession
        tasks = await session.scalars(
            statement=select(Task).filter(Task.user_id == callback.from_user.id, Task.is_done == True)
        )
        tasks = list(tasks.all())
        if tasks:
            for task in tasks:  # type: Task
                await callback.message.answer(
                    text=task.info,
                    reply_markup=task_detail_ikb(task=task) if not task.is_done else None
                )
        else:
            await callback.message.answer(
                text="Задач не найдено!",
                reply_markup=task_panel_ikb
            )


@router.callback_query(F.data == "task_undone")
async def task_undone_list_all(callback: CallbackQuery):
    await callback.message.delete()
    async with async_session_maker() as session:  # type: AsyncSession
        tasks = await session.scalars(
            statement=select(Task).filter(Task.user_id == callback.from_user.id, Task.is_done == False)
        )
        tasks = list(tasks.all())
        if tasks:
            for task in tasks:  # type: Task
                await callback.message.answer(
                    text=task.info,
                    reply_markup=task_detail_ikb(task=task) if not task.is_done else None
                )
        else:
            await callback.message.answer(
                text="Задач не найдено!",
                reply_markup=task_panel_ikb
            )


@router.callback_query(TaskCallbackData.filter(F.action == "del"))
async def del_task(callback: CallbackQuery, callback_data: TaskCallbackData, state: FSMContext):
    await state.clear()
    await state.set_state(state=TaskStatesGroup.delete.approve)
    await state.update_data(task_id=callback_data.id)
    await callback.message.edit_text(
        text="Уверены что хотите удалить задачу?",
        reply_markup=approve_ikb
    )


@router.callback_query(TaskStatesGroup.delete.approve, F.data == "no")
async def revoke_task_del(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    async with async_session_maker() as session:  # type: AsyncSession
        task = await session.get(entity=Task, ident=state_data.get("task_id"))
        if task:
            await callback.message.edit_text(
                text=task.info,
                reply_markup=task_detail_ikb(task=task)
            )


@router.callback_query(TaskStatesGroup.delete.approve, F.data == "yes")
async def approve_task_del(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    await callback.message.delete()
    async with async_session_maker() as session:  # type: AsyncSession
        await session.execute(delete(Task).filter(Task.id == state_data.get("task_id")))
        await session.commit()


@router.callback_query(TaskCallbackData.filter(F.action == "cancel"))
async def cancel_task(callback: CallbackQuery, callback_data: TaskCallbackData, state: FSMContext):
    await state.clear()
    await state.set_state(state=TaskStatesGroup.cancel.approve)
    await state.update_data(task_id=callback_data.id)
    await callback.message.edit_text(
        text="Уверены что задача выполнена?",
        reply_markup=approve_ikb
    )


@router.callback_query(TaskStatesGroup.cancel.approve, F.data == "no")
async def revoke_task_cancel(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    async with async_session_maker() as session:  # type: AsyncSession
        task = await session.get(entity=Task, ident=state_data.get("task_id"))
        if task:
            await callback.message.edit_text(
                text=task.info,
                reply_markup=task_detail_ikb(task=task)
            )


@router.callback_query(TaskStatesGroup.cancel.approve, F.data == "yes")
async def approve_task_cancel(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    async with async_session_maker() as session:  # type: AsyncSession
        task = await session.get(entity=Task, ident=state_data.get("task_id"))
        if task:
            task.is_done = True
            await session.commit()
            await session.refresh(instance=task)
            await callback.message.edit_text(
                text=task.info,
            )
