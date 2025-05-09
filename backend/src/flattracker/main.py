import asyncio

from flattracker.database_manager import DatabaseManager
from flattracker.llm_processor import LLMProcessor
from flattracker.message_processor import MessageProcessor
from flattracker.schema import DATA_SCHEMA
from flattracker.tg_extractor import TelegramExtractor

GROUP_NAMES = ["Megapolis_Hinjewadi_Pune"]


class Orchestrator:
    def __init__(self) -> None:
        self.telegram_extractor = TelegramExtractor(channel_name=GROUP_NAMES[0])
        self.message_processor = MessageProcessor()
        self.db_manager = DatabaseManager()
        self.llm_processor = LLMProcessor()
        self.schema = DATA_SCHEMA

    async def cache_check(self, message: dict) -> bool:
        """Check if the message has already been stored in DB"""
        cached_data = await self.db_manager.get_message_by_text(message)
        if cached_data:
            # if a cache hit happens, then update the date of the message with the latest one
            # convert both datetimes to offset naive i.e. without timezone information
            if cached_data["original_message"]["date"] < message["date"].replace(
                tzinfo=None
            ):
                await self.db_manager.update_record_timestamp(
                    cached_data["original_message"]["id"], message["date"]
                )
            sender_name = cached_data.get("original_message", {}).get("author", "")
            print(f"Cache hit. Sender name: {sender_name}")
            return False
        return True

    async def initialize(self) -> None:
        """initialize all components"""
        await self.db_manager.initialize()

    async def process_batch(self, batch_size: int = 50, offset_id: int = 0) -> int:
        """Process a batch of messages end to end"""
        raw_messages = await self.telegram_extractor.extract_messages(
            limit=batch_size, offset_id=offset_id
        )

        if not raw_messages:
            print("No messages to process")
            return 0

        # preprocess messages
        processed_messages = self.message_processor.batch_process(raw_messages)

        # cache check
        cache_misses = [
            message for message in processed_messages if await self.cache_check(message)
        ]

        # structured data
        structured_data = self.llm_processor.batch_process(cache_misses, self.schema)

        # prepare final data for storage
        final_data = []
        for i, data in enumerate(structured_data):
            if isinstance(data, list):
                for d in data:
                    d["original_message"] = cache_misses[i]
                    final_data.append(d)
            else:
                data["original_message"] = cache_misses[i]
                final_data.append(data)

        # store in database
        await self.db_manager.store_messages(final_data)
        return len(final_data)

    async def run(self, batch_size: int = 10):
        await self.initialize()
        a = await self.process_batch(batch_size)
        return a


async def main():
    orc = Orchestrator()
    ans = await orc.run(50)
    print(ans)


if __name__ == "__main__":
    asyncio.run(main())
