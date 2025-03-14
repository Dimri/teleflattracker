import re
import json
import os

from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMProcessor:
    def __init__(self, api_key=os.getenv("OPENAI_API_KEY")) -> None:
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    def extract_structured_data(self, message: dict, schema: dict) -> str | None:
        """extract structured data from message using LLM"""
        prompt = self._build_prompt(message, schema)

        try:
            output = self.infer_llm(prompt)
            return output
        except Exception as e:
            print(f"Error processing message with LLM: {e}")
            raise

    def infer_llm(self, prompt: str) -> str | None:
        completion = self.client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            messages=[
                {
                    "role": "system",
                    "content": "Extract structured information from the given message according to the provided schema.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return completion.choices[0].message.content

    def _build_prompt(self, message: dict, schema: dict) -> str:
        schema_description = "\n".join(
            f"- {key}: {value}" for key, value in schema.items()
        )
        return f"""Extract the following information from this message:
        {schema_description}
        Return the information as JSON object. If the text doesn't contain any information, leave the value field blank.
        
        Message:
        Text: {message.get("text")}
        """

    def extract_json(self, text: str | None) -> dict:
        pat = re.compile(r"```json\s*\n([\s\S]*?)\n```")
        matches = re.findall(pat, text or "")
        try:
            obj = json.loads(matches[0])
        except Exception:
            print(f"No JSON found in this: {text}")
            obj = {}

        return obj

    def batch_process(self, messages: list[dict], schema: dict) -> list[dict]:
        """process a batch of messages"""
        results: list[dict] = []
        for message in tqdm(messages):
            result = self.extract_structured_data(message, schema)
            result_json = self.extract_json(result)
            results.append(result_json)

        print(f"Processed {len(results)} messages with LLM")
        return results


if __name__ == "__main__":
    pass
