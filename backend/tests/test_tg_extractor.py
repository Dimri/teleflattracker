import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from flattracker.tg_extractor import TelegramExtractor


@pytest.mark.asyncio
async def test_extract_messages_returns_expected_format():
    mock_message = AsyncMock()
    mock_message.id = 1
    mock_message.date = "2023-10-01"
    mock_message.message = "Test message"
    mock_message.sender.first_name = "John"
    mock_message.sender.last_name = "Doe"

    with patch("flattracker.tg_extractor.TelegramClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_client

        mock_client.get_entity.return_value = "channel_entity"
        mock_client.get_messages.return_value = [mock_message]

        extractor = TelegramExtractor("some_channel")
        results = await extractor.extract_messages(limit=1)

        expected = [
            {
                "id": 1,
                "date": "2023-10-01",
                "text": "Test message",
                "sender_first_name": "John",
                "sender_last_name": "Doe",
            }
        ]

        assert isinstance(results, list)
        assert results == expected


@pytest.mark.asyncio
async def test_extract_messages_handles_exceptions():
    with patch("flattracker.tg_extractor.TelegramClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_client
        mock_client.get_entity.side_effect = Exception("Some Error")

        extractor = TelegramExtractor("bad_channel")

        with pytest.raises(Exception) as excinfo:
            await extractor.extract_messages(limit=1)

        assert "Some Error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_extract_messages_with_empty_message():
    extractor = TelegramExtractor(channel_name="test_channel")

    # mock TelegramClient and its methods
    mock_client = AsyncMock()
    mock_client.get_entity = AsyncMock(
        return_value=dict(id=123, title="channel_entity")
    )

    # mock messages with no text
    mock_message = MagicMock()
    mock_message.id = 1
    mock_message.date = datetime(2023, 1, 1)
    mock_message.message = None
    mock_message.sender.first_name = "John"
    mock_message.sender.last_name = "Doe"

    mock_client.get_messages = AsyncMock(return_value=[mock_message])

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "flattracker.tg_extractor.TelegramClient",
            lambda *args, **kwargs: mock_client,
        )

        # act
        results = await extractor.extract_messages(limit=1, offset_id=0)

        # assert
        assert len(results) == 0
