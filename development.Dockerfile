# Base image
FROM python:3.11

RUN apt-get update
#RUN apt-get install -y software-properties-common add-apt-repository -y ppa:alex-p/tesseract-ocr
RUN apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev
RUN apt-get install -y tesseract-ocr-all
RUN apt-get install -y python3-pip python3-minimal libsm6 libxext6
RUn apt-get install -y libgl1
# To make sure that tesseract-ocr is installed, uncomment the following line.
RUN tesseract --version