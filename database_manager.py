from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped


class Base(DeclarativeBase):
    pass


class MessageData(Base):
    __tablename__ = "message_data"
    id: Mapped[int] = Column(Integer, primary_key=True)
    raw_text: Mapped[str] = Column(String)
    structured_data = Column(JSON)
    processed_at = Column(DateTime, default=datetime.now())


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
                        raw_text=data.get("original_message", {}).get("text", ""),
                        structured_data=data.get("structured_data"),
                        processed_at=datetime.now(),
                    )
                    session.add(message)
            await session.commit()
        print(f"Stored {len(processed_data)} messages in database")
