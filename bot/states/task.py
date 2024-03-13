from aiogram.fsm.state import State, StatesGroup


class CreateTaskStatesGroup(StatesGroup):
    title = State()
    description = State()
    end_date = State()


class EditTaskStatesGroup(StatesGroup):
    title = State()
    description = State()
    end_date = State()


class DeleteTaskStatesGroup(StatesGroup):
    approve = State()


class CancelTaskStatesGroup(StatesGroup):
    approve = State()


class TaskStatesGroup(StatesGroup):
    create = CreateTaskStatesGroup
    edit = EditTaskStatesGroup
    delete = DeleteTaskStatesGroup
    cancel = CancelTaskStatesGroup
