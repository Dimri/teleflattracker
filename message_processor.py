from datetime import datetime

import emoji


class MessageProcessor:
    def __init__(self) -> None:
        self.processed_count = 0

    def preprocess_message(self, message: dict) -> dict:
        """clean and normalize a single message"""
        processed = message.copy()

        # convert date to ISO format string
        if isinstance(processed.get("date"), datetime):
            processed["date"] = processed["date"].isoformat()

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
        self.processed_count += len(processed_messages)
        print(f"Processed {len(processed_messages)} messages")
        return processed_messages


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
