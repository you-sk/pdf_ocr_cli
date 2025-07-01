#!/bin/bash
# This script builds the Docker image and runs the tests inside a container.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Building Docker image with test files..."
docker build -t pdf-ocr-cli .

echo "--- Creating test PDFs inside Docker container ---"
# Run the PDF creation script inside the container
docker run --rm --entrypoint python3 -v "$(pwd)":/app pdf-ocr-cli /app/create_test_pdf.py

echo "--- Running tests inside Docker container ---"
# We override the entrypoint to run the unittest module.
# The -v flag provides verbose output from the tests.
docker run --rm --entrypoint python3 -v "$(pwd)":/app pdf-ocr-cli -m unittest discover -v

echo "--- Test run finished ---"
