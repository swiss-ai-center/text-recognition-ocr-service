# Test recognition (OCR) Service

This service extracts text from an image using Tesseract 5. The image is assumed to be a scanned document, 
already resized to appear flat and in the right orientation, submitted as png or jpg.
The output is returned as a json file containing the plain text as well as detected words and their bounding boxes.
The file is structured as follows:

TODO: add JSON structure
