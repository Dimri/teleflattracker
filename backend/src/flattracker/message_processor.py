import emoji

from flattracker.tg_extractor import TGResult


class MessageProcessor:
    def __init__(self) -> None:
        self.processed_count = 0

    def preprocess_message(self, message: TGResult) -> dict:
        """clean and normalize a single message"""
        processed = message.copy()

        if processed.get("text"):
            # clean text: remove emojis, and extra newlines
            processed["text"] = self._clean_text(processed["text"])

        # create a new key name that consist of first name + last name
        processed["sender_name"] = " ".join(
            filter(
                None, [processed["sender_first_name"], processed["sender_last_name"]]
            )
        )

        return processed

    def _clean_text(self, text: str) -> str:
        """clean message text"""
        # remove nbsp with regular space
        text = text.replace("\xa0", " ")
        # remove emojis and strip whitespaces at the ends
        return emoji.replace_emoji(text, "").strip()

    def filter_message(self, message: TGResult) -> bool:
        flag1 = len(message["text"]) > 50
        flag2 = "changed" not in message["text"].lower()
        flag3 = "lead" not in message["text"].lower()
        flag4 = "external" not in message["text"].lower()
        return flag1 and flag2 and flag3 and flag4

    def batch_process(self, messages: list[TGResult]) -> list[dict]:
        """Process a batch of messages"""
        processed_messages: list[dict] = [
            self.preprocess_message(msg) for msg in messages if self.filter_message(msg)
        ]
        # remove duplicate messages
        unique_dicts = list({d["text"]: d for d in processed_messages}.values())
        self.processed_count += len(unique_dicts)
        print(f"Processed {len(unique_dicts)} messages")
        return unique_dicts


if __name__ == "__main__":
    with open("output.txt", "r") as f:
        text = f.read()

    text_list = text.split("-" * 50)
    text2 = [t for t in text_list if t.strip()]

    inputs = []
    for t in text2:
        inputs.append({"text": t, "sender_first_name": None, "sender_last_name": None})

    mp = MessageProcessor()
    outputs = mp.batch_process(inputs)
    for _out in outputs:
        print(_out["text"])
        print("-" * 50)
