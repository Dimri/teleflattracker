from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import select

from flattracker.database_manager import Base, DatabaseManager, MessageData


@pytest_asyncio.fixture
async def db_manager():
    manager = DatabaseManager(db_url="sqlite+aiosqlite:///:memory:")
    await manager.initialize()
    yield manager
    await manager.engine.dispose()


@pytest.mark.asyncio
async def test_initialize_create_tables(db_manager):
    async with db_manager.session_factory() as session:
        result = await session.execute(select(MessageData))
        assert result is not None
        assert "message_data" in Base.metadata.tables
        columns = Base.metadata.tables["message_data"].columns.keys()
        assert set(columns) == {"id", "raw_text", "date", "author", "structured_data"}


@pytest.mark.asyncio
async def test_store_messages_single(db_manager):
    """Test storing a single message in database"""
    message_data = {
        "original_message": {
            "date": datetime(2023, 10, 1),
            "text": "My name is John Doe",
            "sender_name": "Akash Kumar",
        },
        "extra_field": {
            "name": "John Doe",
            "age": 30,
            "location": "New York",
        },
    }

    await db_manager.store_messages([message_data])

    async with db_manager.session_factory() as session:
        result = await session.execute(select(MessageData))
        messages = result.scalars().all()
        assert len(messages) == 1
        assert messages[0].raw_text == "My name is John Doe"
        assert messages[0].author == "Akash Kumar"
        assert messages[0].date == datetime(2023, 10, 1)
        assert messages[0].structured_data == {
            "extra_field": {
                "name": "John Doe",
                "age": 30,
                "location": "New York",
            }
        }


@pytest.mark.asyncio
async def test_store_messages_multiple(db_manager):
    """Test storing multiple messages."""
    message_data = [
        {
            "original_message": {
                "date": datetime(2023, 1, 1),
                "text": "First message",
                "sender_name": "Bob",
            }
        },
        {
            "original_message": {
                "date": datetime(2023, 1, 2),
                "text": "Second message",
                "sender_name": "Alice",
            }
        },
    ]
    await db_manager.store_messages(message_data)

    async with db_manager.session_factory() as session:
        result = await session.execute(select(MessageData))
        messages = result.scalars().all()

        assert len(messages) == 2
        assert messages[0].raw_text == "First message"
        assert messages[0].author == "Bob"
        assert messages[0].date == datetime(2023, 1, 1)
        assert messages[1].raw_text == "Second message"
        assert messages[1].author == "Alice"
        assert messages[1].date == datetime(2023, 1, 2)


@pytest.mark.asyncio
async def test_store_messages_empty(db_manager):
    """Test storing an empty list of messages."""
    await db_manager.store_messages([])

    async with db_manager.session_factory() as session:
        result = await session.execute(select(MessageData))
        messages = result.scalars().all()
        assert len(messages) == 0


@pytest.mark.asyncio
async def test_store_messages_missing_fields(db_manager):
    """Test storing messages with missing fields."""
    message_data = {
        "original_message": {
            "text": "Message without sender",
        },
        "extra_field": {
            "name": "John Doe",
            "age": 30,
            "location": "New York",
        },
    }

    await db_manager.store_messages([message_data])

    async with db_manager.session_factory() as session:
        result = await session.execute(select(MessageData))
        messages = result.scalars().all()
        assert len(messages) == 1
        assert messages[0].raw_text == "Message without sender"
        assert messages[0].author == ""
        assert messages[0].date is None
        assert messages[0].structured_data == {
            "extra_field": {
                "name": "John Doe",
                "age": 30,
                "location": "New York",
            }
        }


@pytest.mark.asyncio
async def test_get_message_by_text(db_manager):
    """Test retrieving a message by text when it exists."""
    message_data = [
        {
            "original_message": {
                "date": datetime(2023, 1, 1),
                "text": "Test message",
                "sender_name": "Charlie",
            },
            "metadata": "some_data",
        }
    ]
    await db_manager.store_messages(message_data)

    result = await db_manager.get_message_by_text({"text": "Test message"})
    assert result is not None
    assert result["original_message"]["raw_text"] == "Test message"
    assert result["original_message"]["author"] == "Charlie"
    assert result["original_message"]["date"] == datetime(2023, 1, 1)


@pytest.mark.asyncio
async def test_get_message_by_text_not_found(db_manager):
    """Test retrieving a message by text when it doesn't exist."""
    result = await db_manager.get_message_by_text({"text": "Test message"})
    assert result is None


@pytest.mark.asyncio
async def test_update_record_timestamp_success(db_manager):
    """Test updating a record's timestamp."""
    message_data = {
        "original_message": {
            "date": datetime(2023, 1, 1),
            "text": "Message to update",
            "sender_name": "David",
        },
    }
    await db_manager.store_messages([message_data])

    async with db_manager.session_factory() as session:
        result = await session.execute(select(MessageData))
        message = result.scalars().first()

    new_timestamp = datetime(2023, 2, 1)
    await db_manager.update_record_timestamp(message.id, new_timestamp)

    # Verify the update
    async with db_manager.session_factory() as session:
        result = await session.execute(
            select(MessageData).where(MessageData.id == message.id)
        )
        updated_message = result.scalars().one()
        assert updated_message.date == new_timestamp


