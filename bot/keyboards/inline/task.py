from typing import Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pydantic import PositiveInt

from src.models import Task

task_panel_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="ВСЕ", callback_data="task_all"),
            InlineKeyboardButton(text="ВЫПОЛНЕННЫЕ", callback_data="task_done"),
        ],
        [
            InlineKeyboardButton(text="НЕ ВЫПОЛНЕННЫЕ", callback_data="task_undone"),
        ]
    ]
)

approve_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="ДА", callback_data="yes"),
            InlineKeyboardButton(text="НЕТ", callback_data="no"),
        ]
    ]
)


class TaskCallbackData(CallbackData, prefix="task"):
    id: PositiveInt
    action: Literal["del", "edit", "cancel", "approve"]


def task_detail_ikb(task: Task) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅",
                    callback_data=TaskCallbackData(id=task.id, action="cancel").pack()
                ),
                InlineKeyboardButton(
                    text="❎",
                    callback_data=TaskCallbackData(id=task.id, action="del").pack()
                ),
            ]
        ]
    )
