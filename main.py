import json
import asyncio

from database_manager import DatabaseManager
from llm_processor import LLMProcessor
from message_processor import MessageProcessor
from schema import DATA_SCHEMA
from tg_extractor import TelegramExtractor

from itertools import chain

GROUP_NAMES = ["Megapolis_Hinjewadi_Pune"]


class Orchestrator:
    def __init__(self) -> None:
        self.telegram_extractor = TelegramExtractor(channel_name=GROUP_NAMES[0])
        self.message_processor = MessageProcessor()
        self.llm_processor = LLMProcessor()
        self.db_manager = DatabaseManager()
        self.schema = DATA_SCHEMA

    async def initialize(self) -> None:
        """initialize all components"""
        await self.db_manager.initialize()
        print("All components initialized")

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

        # structured data
        structured_data = self.llm_processor.batch_process(
            processed_messages, self.schema
        )

        with open("out.json", "w") as f:
            json.dump(structured_data, f, indent=4)

        # flatten the structured_data list
        structured_data = list(
            chain.from_iterable(
                data if isinstance(data, list) else [data] for data in structured_data
            )
        )

        # prepare final data for storage
        final_data = []
        for i, data in enumerate(structured_data):
            data["original_message"] = processed_messages[i]
            final_data.append(data)

        # store in database
        await self.db_manager.store_messages(final_data)
        return len(final_data)


async def main():
    orc = Orchestrator()
    ans = await orc.process_batch(10)
    print(ans)


if __name__ == "__main__":
    asyncio.run(main())
