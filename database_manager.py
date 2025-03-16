from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class MessageData(Base):
    __tablename__ = "message_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_text: Mapped[str] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(DateTime)
    author: Mapped[str] = mapped_column(String)

    structured_data = mapped_column(JSON)


class DatabaseManager:
    def __init__(self, db_url="sqlite+aiosqlite:///telegram_data.db") -> None:
        self.engine = create_async_engine(db_url)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def initialize(self) -> None:
        """create tables if they don't exist"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialized")

    async def store_messages(self, processed_data: list[dict]) -> None:
        """store processed messages in the database"""
        async with self.session_factory() as session:
            async with session.begin():
                for data in processed_data:
                    message = MessageData(
                        date=data.get("original_message", {}).get("date"),
                        raw_text=data.get("original_message", {}).get("text", ""),
                        author=data.get("original_message", {}).get("sender_name", ""),
                        structured_data={
                            k: v for k, v in data.items() if k != "original_message"
                        },
                    )
                    session.add(message)
            await session.commit()
        print(f"Stored {len(processed_data)} messages in database")

    async def get_message_by_text(self, message: dict) -> dict | None:
        """retrieve message dict by raw text"""
        async with self.session_factory() as session:
            statement = select(MessageData).where(
                MessageData.raw_text == message["text"]
            )
            result_obj = await session.execute(statement)
            result = result_obj.scalar_one_or_none()
            if result:
                val = result.structured_data
                val["original_message"] = {
                    "id": result.id,
                    "date": result.date,
                    "raw_text": result.raw_text,
                    "author": result.author,
                }
                return val
            return None

    async def update_record_timestamp(self, id: int, val: Any) -> None:
        async with self.session_factory() as session:
            statement = update(MessageData).where(MessageData.id == id).values(date=val)
            result = await session.execute(statement)
            await session.commit()
            print(f"Rows updated: {result.rowcount}")
