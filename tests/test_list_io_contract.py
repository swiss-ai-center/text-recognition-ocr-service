import json
from types import SimpleNamespace

import pytest
from common_code.common.enums import FieldDescriptionType

import my_service as my_service_module
from my_service import MyService


class FakeDataPoint:
    def __init__(self, text: str):
        self.text = text

    def to_dict(self):
        return {"text": self.text}


class FakeTextRecognition:
    def image_to_data(self, data, img_type):
        return [FakeDataPoint(data.decode("utf-8"))]

    def image_to_string(self, data, language=None):
        return data.decode("utf-8")


def make_input_item(text: str, field_type: FieldDescriptionType = FieldDescriptionType.IMAGE_PNG):
    return SimpleNamespace(data=text.encode("utf-8"), type=field_type)


def parse_result_text(result_item):
    return json.loads(result_item.data)["text"]


def test_allow_lists_defaults_to_true():
    service = MyService()

    assert service.allow_lists is True


def test_single_item_input_is_normalized_to_list_of_one(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(my_service_module, "TextRecognition", FakeTextRecognition)
    service = MyService()

    output = service.process({"image": make_input_item("one")})

    assert isinstance(output["result"], list)
    assert len(output["result"]) == 1
    assert parse_result_text(output["result"][0]) == "one"


def test_multi_item_input_is_processed_and_returns_a_list(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(my_service_module, "TextRecognition", FakeTextRecognition)
    service = MyService()

    output = service.process(
        {
            "image": [
                make_input_item("first"),
                make_input_item("second"),
            ]
        }
    )

    assert isinstance(output["result"], list)
    assert [parse_result_text(item) for item in output["result"]] == ["first", "second"]
    assert all(not isinstance(item, list) for item in output["result"])


def test_nested_list_input_is_rejected(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(my_service_module, "TextRecognition", FakeTextRecognition)
    service = MyService()

    with pytest.raises(
        ValueError,
        match="field 'image' must be a 1D list \(lists of lists are not allowed\)",
    ):
        service.process({"image": [[make_input_item("nested")]]})


def test_allow_lists_false_rejects_multi_item_input(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(my_service_module, "TextRecognition", FakeTextRecognition)
    service = MyService()
    service.allow_lists = False

    with pytest.raises(
        ValueError,
        match="field 'image' must contain exactly one item when allow_lists is false",
    ):
        service.process({"image": [make_input_item("first"), make_input_item("second")]})


def test_allow_lists_false_accepts_single_item_list(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(my_service_module, "TextRecognition", FakeTextRecognition)
    service = MyService()
    service.allow_lists = False

    output = service.process({"image": [make_input_item("single")]})

    assert isinstance(output["result"], list)
    assert len(output["result"]) == 1
    assert parse_result_text(output["result"][0]) == "single"
