from datetime import datetime

from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, TIMESTAMP, CheckConstraint, BOOLEAN, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    ...


class User(Base):
    __tablename__ = "bot_users"

    id = Column(BIGINT, primary_key=True)

    tasks = relationship(argument="Task", back_populates="user")


class Task(Base):
    __tablename__ = "bot_tasks"
    __table_args__ = (
        CheckConstraint("end_date > start_date"),
    )

    id = Column(BIGINT, primary_key=True)
    title = Column(VARCHAR(length=128), nullable=False)
    description = Column(TEXT, nullable=True)
    start_date = Column(TIMESTAMP, default=datetime.now, server_default="now()", nullable=False)
    end_date = Column(TIMESTAMP, nullable=False)
    is_done = Column(BOOLEAN, default=False, nullable=False, server_default="false")
    user_id = Column(
        BIGINT,
        ForeignKey("bot_users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        default=608287610
    )

    user = relationship(argument=User, back_populates="tasks")

    def __str__(self) -> str:
        return self.title

    @property
    def info(self) -> str:
        return (f"<b>{self.title}</b>\n\n"
                f"<i>{self.description or ''}</i>\n\n"
                f"Дата начала: {self.start_date.strftime('%d.%m.%Y %H:%M')}\n"
                f"Дата окончания: {self.end_date.strftime('%d.%m.%Y %H:%M')}\n"
                f"Статус: {'✅' if self.is_done else '❎'}"
                )
