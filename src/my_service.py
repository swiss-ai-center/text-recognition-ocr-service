from common_code.config import get_settings
from common_code.logger.logger import get_logger, Logger
from common_code.service.models import Service
from common_code.service.enums import ServiceStatus
from common_code.common.enums import FieldDescriptionType, ExecutionUnitTagName, ExecutionUnitTagAcronym
from common_code.common.models import FieldDescription, ExecutionUnitTag
from common_code.tasks.models import TaskData
# Imports required by the service's model
from text_recognition.text_recognition import TextRecognition
from text_recognition.text_recognition import CustomEncoder

api_description = """This service extracts text from an image using Tesseract 5.
The image is assumed to be a scanned document,
already resized to appear flat and in the right orientation, submitted as png or jpg.
The output is returned as a json file containing the plain text as well as detected words and their bounding boxes.
"""
api_summary = """Returns a JSON file containing the text in the input image and its position.
"""
api_title = "Text Recognition OCR API."
version = "0.0.1"

settings = get_settings()


class MyService(Service):
    """
    OCR service model
    """

    # Any additional fields must be excluded for Pydantic to work
    _model: object
    _logger: Logger

    def __init__(self):
        super().__init__(
            name="Text Recognition OCR",
            slug="text-recognition-ocr",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,

            data_in_fields=[
                FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
            ],
            data_out_fields=[
                FieldDescription(
                    name="result", type=[FieldDescriptionType.APPLICATION_JSON]
                ),
            ],
            tags=[
                ExecutionUnitTag(
                    name=ExecutionUnitTagName.IMAGE_PROCESSING,
                    acronym=ExecutionUnitTagAcronym.IMAGE_PROCESSING,
                ),
            ],
            has_ai=True,
            docs_url="https://docs.swiss-ai-center.ch/reference/services/text-recognition-ocr/",
        )
        self._logger = get_logger(settings)

    def process(self, data):
        # NOTE that the data is a dictionary with the keys being the field names set in the data_in_fields
        # The objects in the data variable are always bytes. It is necessary to convert them to the desired type
        # before using them.
        # raw = data["image"].data
        # input_type = data["image"].type
        # ... do something with the raw data

        tr = TextRecognition()
        img_data = tr.image_to_data(data=data['image'].data, img_type=data['image'].type)
        img_data = [dp.to_dict() for dp in img_data if len(dp.text) > 0]
        text_data = tr.image_to_string(data=data['image'].data)

        json_data = {'text': text_data,
                     'boxes': img_data}
        json_data = CustomEncoder().encode(json_data)

        # NOTE that the result must be a dictionary with the keys being the field names set in the data_out_fields
        return {
            "result": TaskData(data=json_data, type=FieldDescriptionType.APPLICATION_JSON),
        }
