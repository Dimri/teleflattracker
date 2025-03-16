import emoji


class MessageProcessor:
    def __init__(self) -> None:
        self.processed_count = 0

    def preprocess_message(self, message: dict) -> dict:
        """clean and normalize a single message"""
        processed = message.copy()

        # clean text: remove emojis, and extra newlines
        if processed.get("text"):
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

    def filter_message(self, message: dict[str, str]) -> bool:
        flag1 = len(message["text"]) > 50
        flag2 = "changed" not in message["text"].lower()
        return flag1 and flag2

    def batch_process(self, messages: list[dict]) -> list[dict]:
        """Process a batch of messages"""
        processed_messages = [
            self.preprocess_message(msg) for msg in messages if self.filter_message(msg)
        ]
        # remove duplicate messages
        unique_dicts = {d["text"]: d for d in processed_messages}.values()
        unique_dicts = list(unique_dicts)
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
