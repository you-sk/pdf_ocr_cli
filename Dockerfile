FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-jpn \
    poppler-utils \
    pkg-config \
    build-essential \
    libgl1-mesa-glx \
    fonts-ipafont-gothic \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV TESSDATA_PREFIX /usr/share/tesseract-ocr/4.00/tessdata
ENV PATH="/usr/bin:${PATH}"

ENTRYPOINT ["python", "/app/pdf_ocr_tool.py"]

