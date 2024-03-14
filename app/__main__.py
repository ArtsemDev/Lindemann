from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi import Path as PathParam
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from orjson import orjson
from pydantic import BaseModel, Field, field_validator, PositiveInt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.auth.telegram import TelegramWebappAuthenticationBackend
from src.models import Task
from src.settings import async_session_maker, settings

BASE_DIR = Path(__file__).resolve().parent.parent
templating = Jinja2Templates(directory=BASE_DIR / "templates")
statics = StaticFiles(directory=BASE_DIR / "statics")


class TaskCreateForm(BaseModel):
    title: str = Field(default=..., max_length=128)
    description: Optional[str]
    end_date: datetime

    @field_validator("end_date", mode="after")
    def validate_end_date(cls, value: datetime):
        if value < datetime.now():
            raise ValueError("Дата окончания не может быть меньше текущей даты")
        return value


class TaskDetail(BaseModel):
    id: PositiveInt
    is_done: bool
    start_date: datetime
    title: str = Field(default=..., max_length=128)
    description: Optional[str]
    end_date: datetime


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    include_in_schema=False
)
app.add_middleware(middleware_class=ProxyHeadersMiddleware, trusted_hosts=("*", ))
app.add_middleware(
    middleware_class=AuthenticationMiddleware,
    backend=TelegramWebappAuthenticationBackend(token=settings.BOT_TOKEN.get_secret_value(), loads=orjson.loads)
)
app.mount(path="/statics", app=statics, name="statics")


@app.get(path="/", response_class=HTMLResponse)
async def index(request: Request):
    return templating.TemplateResponse(request=request, name="index.html")


@app.post(path="/", response_class=ORJSONResponse, response_model=TaskDetail, status_code=201)
async def create_task(request: Request, form: TaskCreateForm):
    async with async_session_maker() as session:  # type: AsyncSession
        form.end_date = form.end_date.replace(tzinfo=None)
        task = Task(**form.model_dump() | {"user_id": request.user.id})
        session.add(instance=task)
        try:
            await session.commit()
        except IntegrityError:
            raise HTTPException(status_code=422, detail="Шото пошло не так!")
        else:
            await session.refresh(instance=task)
            return TaskDetail.model_validate(obj=task, from_attributes=True)


@app.get(path="/tasks", response_model=list[TaskDetail], response_class=ORJSONResponse)
async def user_tasks(request: Request, q: str = Query(default=None)):
    async with async_session_maker() as session:  # type: AsyncSession
        stmt = select(Task).filter(Task.user_id == request.user.id)
        if q:
            stmt = stmt.filter(Task.title.icontains(q.lower()))
        tasks = await session.scalars(
            statement=stmt
        )
        return [TaskDetail.model_validate(obj=task, from_attributes=True) for task in tasks.all()]


if __name__ == '__main__':
    from uvicorn import run
    run(app=app, host="0.0.0.0", port=80)
