# Base image
FROM python:3.11

#RUN add-apt-repository ppa:alex-p/tesseract-ocr5
RUN apt-get update
#RUN apt-cache madison tesseract-ocr
#RUN apt-get install -y software-properties-common add-apt-repository -y ppa:alex-p/tesseract-ocr
RUN apt-get install -y tesseract-ocr=5.3.0-2
RUN apt-get install -y libtesseract-dev libleptonica-dev
RUN apt-get install -y tesseract-ocr-all
RUN apt-get install -y python3-pip python3-minimal libsm6 libxext6
RUN apt-get install -y libgl1
# To make sure that tesseract-ocr is installed, uncomment the following line.
RUN tesseract --version