from unittest.mock import MagicMock, Mock, patch

import pytest

from flattracker.llm_processor import LLMProcessor


@pytest.fixture
def llm_processor():
    with patch("flattracker.llm_processor.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_client.api_key = "test_api_key"
        mock_client.base_url = "https://openrouter.ai/api/v1/"
        mock_openai.return_value = mock_client
        processor = LLMProcessor(api_key="test_api_key")
        processor._mock_client = mock_client
        yield processor


def test_init(llm_processor):
    assert isinstance(llm_processor.client, Mock)
    assert llm_processor.client.api_key == "test_api_key"
    assert llm_processor.client.base_url == "https://openrouter.ai/api/v1/"


def test_build_prompt(llm_processor):
    message = {"text": "This is a test message."}
    schema = {"name": "string", "age": "integer"}
    prompt = llm_processor._build_prompt(message, schema)

    expected_prompt = """Extract the following information from this message:
- name: string
- age: integer
Return the information as JSON object. If the text doesn't contain any information, leave the value field blank.

Message:
Text: This is a test message."""

    assert prompt == expected_prompt


def test_build_prompt_empty_message(llm_processor):
    message = {"text": ""}
    schema = {"name": "string", "age": "integer"}
    prompt = llm_processor._build_prompt(message, schema)

    expected_prompt = """Extract the following information from this message:
- name: string
- age: integer
Return the information as JSON object. If the text doesn't contain any information, leave the value field blank.

Message:
Text: """

    assert prompt == expected_prompt


@patch("flattracker.llm_processor.OpenAI")
def test_infer_llm_success(mock_openai, llm_processor):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        """```json\n{"name": "John Doe", "age": 30}\n```"""
    )

    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.return_value = mock_response
    llm_processor = LLMProcessor(api_key="test_api_key")
    result = llm_processor.infer_llm("Test prompt")
    assert result == """```json\n{"name": "John Doe", "age": 30}\n```"""
    mock_client.chat.completions.create.assert_called_once()


@patch("flattracker.llm_processor.OpenAI")
def test_infer_llm_error(mock_openai, llm_processor):
    mock_openai.return_value.chat.completions.create.side_effect = Exception(
        "API Error"
    )

    result = llm_processor.infer_llm("Test prompt")
    assert result is None


def test_extract_json_valid(llm_processor):
    text = """```json\n{"name": "John Doe", "age": 30}\n```"""
    result = llm_processor.extract_json(text)
    assert result == dict(name="John Doe", age=30)


def test_extract_json_invalid(llm_processor):
    text = """{"name": "John Doe" "age": 30}\n"""
    result = llm_processor.extract_json(text)
    assert result == dict()


def test_extract_json_empty(llm_processor):
    text = None
    result = llm_processor.extract_json(text)
    assert result == dict()


@patch("flattracker.llm_processor.LLMProcessor.infer_llm")
def test_extract_structured_data_success(mock_infer_llm, llm_processor):
    message = {"text": "Hello, my name is John Doe and I am 30 years old."}
    schema = {"name": "string", "age": "integer"}
    mock_infer_llm.return_value = """```json\n{"name": "John Doe", "age": 30}\n```"""

    result = llm_processor.extract_structured_data(message, schema)
    assert result == """```json\n{"name": "John Doe", "age": 30}\n```"""
    mock_infer_llm.assert_called_once()


@patch("flattracker.llm_processor.LLMProcessor.infer_llm")
def test_extract_structured_data_error(mock_infer_llm, llm_processor):
    message = {"text": "Hello, my name is John Doe and I am 30 years old."}
    schema = {"name": "string", "age": "integer"}
    mock_infer_llm.side_effect = Exception("LLM Error")

    with pytest.raises(Exception, match="LLM Error"):
        llm_processor.extract_structured_data(message, schema)


# Test batch processing


@patch("flattracker.llm_processor.LLMProcessor.extract_structured_data")
@patch("flattracker.llm_processor.LLMProcessor.extract_json")
def test_batch_process_success(mock_extract_json, mock_structured_data, llm_processor):
    messages = [
        {"text": "Hello, my name is John Doe and I am 30 years old."},
        {"text": "Hello my name is Jane Smith."},
    ]
    schema = {"name": "string", "age": "integer"}
    expected_results = [
        dict(name="John Doe", age=30),
        dict(name="Jane Smith", age=None),
    ]
    mock_structured_data.side_effect = [
        """```json\n{"name": "John Doe", "age": 30}\n```""",
        """```json\n{"name": "Jane Smith", "age": None}\n```""",
    ]
    mock_extract_json.side_effect = expected_results

    with patch("flattracker.llm_processor.tqdm", return_value=messages) as mock_tqdm:
        results = llm_processor.batch_process(messages, schema)
        assert len(results) == 2
        assert results == expected_results
        mock_structured_data.assert_called()
        mock_extract_json.assert_called()
        mock_tqdm.assert_called_once()


@patch("flattracker.llm_processor.LLMProcessor.extract_structured_data")
@patch("flattracker.llm_processor.tqdm")
def test_batch_process_empty(mock_tqdm, mock_structured_data, llm_processor):
    messages = []
    schema = {"name": "string", "age": "integer"}
    mock_structured_data.side_effect = []

    results = llm_processor.batch_process(messages, schema)
    assert len(results) == 0
    mock_tqdm.assert_called_once()
