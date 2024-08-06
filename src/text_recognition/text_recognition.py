
import io
import csv
import pytesseract as pt
from PIL import Image
from typing import cast
from models import *
from common_code.common.enums import FieldDescriptionType
from typing import Union

class TextRecognition:

    def __init__(self) -> None:
        pass

    def image_to_pdf(self, config: DataIn) -> bytes:

        with Image.open(config.image.file) as image:
            return cast(bytes, pt.image_to_pdf_or_hocr(image=image, lang=config.language))

    def image_to_string(self, config: DataIn) -> str:
        with Image.open(config.image.file) as image:
            return pt.image_to_string(image=image, lang=config.language)

    def image_to_data(self, data, img_type: Union[FieldDescriptionType.IMAGE_JPEG, FieldDescriptionType.IMAGE_PNG]) -> list[DataElementOut]:

        imageStream = io.BytesIO(data)
        image = Image.open(imageStream)

        csv_str = pt.image_to_data(image=image)
        reader = csv.DictReader(io.StringIO(csv_str), delimiter="\t", quoting=csv.QUOTE_NONE)

        data_out = []
        for row in reader:
            print(row)
            element_position = DataElementPosition(
                left=int(row["left"]),
                top=int(row["top"]),
                width=int(row["width"]),
                height=int(row["height"])
            )
            data_out.append(
                DataElementOut(
                    level=int(row["level"]),
                    pageNum=int(row["page_num"]),
                    blockNum=int(row["block_num"]),
                    parNum=int(row["par_num"]),
                    lineNum=int(row["line_num"]),
                    wordNum=int(row["word_num"]),
                    position=element_position,
                    confidence=float(row["conf"]),
                    text=row["text"] if row["text"] is not None else "",
                )
            )
        return data_out