import asyncio
import json
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from common_code.config import get_settings
from common_code.http_client import HttpClient
from common_code.logger.logger import get_logger, Logger
from common_code.service.controller import router as service_router
from common_code.service.service import ServiceService
from common_code.storage.service import StorageService
from common_code.tasks.controller import router as tasks_router
from common_code.tasks.service import TasksService
from common_code.tasks.models import TaskData
from common_code.service.models import Service
from common_code.service.enums import ServiceStatus
from common_code.common.enums import FieldDescriptionType, ExecutionUnitTagName, ExecutionUnitTagAcronym
from common_code.common.models import FieldDescription, ExecutionUnitTag
from contextlib import asynccontextmanager
import cv2
import numpy as np

# Imports required by the service's model
from text_recognition import TextRecognition
import io
import csv
import pytesseract as pt
from PIL import Image
from typing import cast
from models import *

import traceback
from fastapi.logger import logger
import logging

settings = get_settings()

# ------- TEMPORARY STUFF -----------
mlogger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)
pt.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'


class MyService(Service):
    """
    OCR service model
    """

    # Any additional fields must be excluded for Pydantic to work
    _model: object
    _logger: Logger

    def __init__(self):
        super().__init__(
            name="Text Recognition",
            slug="text-recognition",
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
                # TODO: put that in another microservice
                #FieldDescription(name="bounding boxes", type=[FieldDescriptionType.IMAGE_PNG])
            ],
            tags=[
                ExecutionUnitTag(
                    name=ExecutionUnitTagName.IMAGE_PROCESSING,
                    acronym=ExecutionUnitTagAcronym.IMAGE_PROCESSING,
                ),
            ],
            has_ai=True,
            # OPTIONAL: CHANGE THE DOCS URL TO YOUR SERVICE'S DOCS
            # docs_url="https://docs.swiss-ai-center.ch/reference/core-concepts/service/",
        )
        self._logger = get_logger(settings)

    def process(self, data):
        try:
            # NOTE that the data is a dictionary with the keys being the field names set in the data_in_fields
            # The objects in the data variable are always bytes. It is necessary to convert them to the desired type
            # before using them.
            # raw = data["image"].data
            # input_type = data["image"].type
            # ... do something with the raw data

            tr = TextRecognition()
            result = tr.image_to_data(data=data['image'].data, img_type=data['image'].type)
            json_data = [d.toJSON() for d in result]
            json_data = json.dumps(json_data)

            #boxes = tr.draw_bounding_boxes(data['image'].data, result)
            #is_ok, out_buff = cv2.imencode('.png', np.array(boxes))
            # NOTE that the result must be a dictionary with the keys being the field names set in the data_out_fields
            return {
                "result": TaskData(data=json_data, type=FieldDescriptionType.APPLICATION_JSON),
                #"bounding boxes": TaskData(data=out_buff.tobytes(), type=FieldDescriptionType.IMAGE_PNG)
            }
        except:
            traceback.print_exc()
            return {
                "result": ""
            }


service_service: ServiceService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Manual instances because startup events doesn't support Dependency Injection
    # https://github.com/tiangolo/fastapi/issues/2057
    # https://github.com/tiangolo/fastapi/issues/425

    # Global variable
    global service_service

    # Startup
    logger = get_logger(settings)
    http_client = HttpClient()
    storage_service = StorageService(logger)
    my_service = MyService()
    tasks_service = TasksService(logger, settings, http_client, storage_service)
    service_service = ServiceService(logger, settings, http_client, tasks_service)

    tasks_service.set_service(my_service)

    # Start the tasks service
    tasks_service.start()

    async def announce():
        retries = settings.engine_announce_retries
        for engine_url in settings.engine_urls:
            announced = False
            while not announced and retries > 0:
                announced = await service_service.announce_service(my_service, engine_url)
                retries -= 1
                if not announced:
                    time.sleep(settings.engine_announce_retry_delay)
                    if retries == 0:
                        logger.warning(
                            f"Aborting service announcement after "
                            f"{settings.engine_announce_retries} retries"
                        )

    # Announce the service to its engine
    asyncio.ensure_future(announce())

    yield

    # Shutdown
    for engine_url in settings.engine_urls:
        await service_service.graceful_shutdown(my_service, engine_url)


api_description = """Returns a JSON file containing the text in the input image and its position.
"""
api_summary = """Returns a JSON file containing the text in the input image and its position.
"""

# Define the FastAPI application with information
app = FastAPI(
    lifespan=lifespan,
    title="Text Recognition API.",
    description=api_description,
    version="0.0.1",
    contact={
        "name": "Swiss AI Center",
        "url": "https://swiss-ai-center.ch/",
        "email": "info@swiss-ai-center.ch",
    },
    swagger_ui_parameters={
        "tagsSorter": "alpha",
        "operationsSorter": "method",
    },
    license_info={
        "name": "GNU Affero General Public License v3.0 (GNU AGPLv3)",
        "url": "https://choosealicense.com/licenses/agpl-3.0/",
    },
)

# Include routers from other files
app.include_router(service_router, tags=["Service"])
app.include_router(tasks_router, tags=["Tasks"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs", status_code=301)
