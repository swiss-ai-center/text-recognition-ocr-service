from pydantic import BaseModel
from fastapi import UploadFile, Form
from enum import Enum
import json


class Language(str, Enum):
    FRENCH = "fra"
    ENGLISH = "eng"
    GERMAN = "deu"
    ITALIAN = "ita"


class DataIn(BaseModel):
    image: UploadFile = Form(description="An image of type png or jpg")
    # language: Language = Form(description="The language of the document")


class DataElementPosition(BaseModel):
    left: int
    top: int
    width: int
    height: int

    def to_dict(self):
        return self.__dict__

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)


class DataElementOut(BaseModel):
    level: int
    pageNum: int
    blockNum: int
    parNum: int
    lineNum: int
    wordNum: int
    position: DataElementPosition
    confidence: float
    text: str

    def toJSON(self):
        self.position = self.position.to_dict()
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)


class TextOut(BaseModel):
    result: str
