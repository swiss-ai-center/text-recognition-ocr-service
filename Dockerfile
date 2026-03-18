# Base image
FROM python:3.11
#FROM ubuntu:18.04
#RUN add-apt-repository ppa:alex-p/tesseract-ocr5
RUN apt-get update
#RUN apt-get install -y software-properties-common add-apt-repository -y ppa:alex-p/tesseract-ocr
RUN apt-get install -y tesseract-ocr
RUN apt-get install -y libtesseract-dev libleptonica-dev
RUN apt-get install -y tesseract-ocr-all

# To make sure that tesseract-ocr is installed, uncomment the following line.
RUN tesseract --version

# Work directory
WORKDIR /app

# Copy requirements file
COPY pyproject.toml uv.lock ./
# Install dependencies
RUN pip install --no-cache-dir uv
RUN uv sync

# Copy sources
COPY src src

# Environment variables
ENV ENVIRONMENT=${ENVIRONMENT}
ENV LOG_LEVEL=${LOG_LEVEL}
ENV ENGINE_URL=${ENGINE_URL}
ENV MAX_TASKS=${MAX_TASKS}
ENV ENGINE_ANNOUNCE_RETRIES=${ENGINE_ANNOUNCE_RETRIES}
ENV ENGINE_ANNOUNCE_RETRY_DELAY=${ENGINE_ANNOUNCE_RETRY_DELAY}

# Exposed ports
EXPOSE 80

# Switch to src directory
WORKDIR "/app/src"

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
ENV PATH="/usr/bin:${PATH}"
ENTRYPOINT ["uv", "run"]
# Command to run on start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
