import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

GROUP_NAMES = ["Megapolis_Hinjewadi_Pune"]


class TelegramExtractor:
    def __init__(
        self,
        channel_name: str,
    ) -> None:
        self.channel_name = channel_name

    async def extract_messages(self, limit: int = 10, offset_id: int = 0) -> list[dict]:
        results = []
        try:
            async with TelegramClient(
                "test", api_hash=os.getenv("API_HASH"), api_id=os.getenv("API_ID")
            ) as client:
                channel_info = await client.get_entity(self.channel_name)
                messages = await client.get_messages(
                    channel_info, limit=limit, offset_id=offset_id
                )
                for message in messages:
                    if message.message:
                        results.append(
                            {
                                "id": message.id,
                                "date": message.date,
                                "text": message.message,
                                "sender_first_name": message.sender.first_name,
                                "sender_last_name": message.sender.last_name,
                            }
                        )
                print(f"Extracted {len(results)} messages")
                return results
        except Exception as e:
            print(f"Error extracting messages: {e}")
            raise


async def main():
    extractor = TelegramExtractor(GROUP_NAMES[0])
    res = await extractor.extract_messages()
    for r in res:
        print(repr(r["text"]))
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
