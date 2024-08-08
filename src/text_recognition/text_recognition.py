# Code based on https://gitlab.forge.hefr.ch/icoservices/deepmarket/image/text-recognition

import io
import csv
import pytesseract as pt
from PIL import Image, ImageDraw
from typing import cast
from models import *

class TextRecognition:

    def __init__(self) -> None:
        pass

    def image_to_pdf(self, config: DataIn) -> bytes:

        with Image.open(config.image.file) as image:
            return cast(bytes, pt.image_to_pdf_or_hocr(image=image, lang=config.language))

    def image_to_string(self, config: DataIn) -> str:
        with Image.open(config.image.file) as image:
            return pt.image_to_string(image=image, lang=config.language)

    def image_to_data(self, data, img_type) -> list[DataElementOut]:

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

    def draw_bounding_boxes(self, data, data_out):
        imageStream = io.BytesIO(data)
        image = Image.open(imageStream)
        image = ImageDraw.Draw(image)
        for elt in data_out:
            box = elt.position
            x, y, w, h = box['left'], box['top'], box['width'], box['height']
            shape = [x, y, x + w, y + h]
            image.rectangle(shape, fill = None, outline="red")
        return image._image
