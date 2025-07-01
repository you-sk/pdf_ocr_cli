#!/bin/bash
# This script builds the Docker image and runs the tests inside a container.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define a temporary directory for test PDFs on the host
TEST_PDF_DIR="$(pwd)/test_pdfs"
mkdir -p "$TEST_PDF_DIR"

echo "Building Docker image with test files..."
docker build -t pdf-ocr-cli .

echo "--- Creating test PDFs inside Docker container ---"
# Run the PDF creation script inside the container, mounting the test_pdfs directory
docker run --rm --entrypoint python3 -v "$TEST_PDF_DIR":/data pdf-ocr-cli /app/create_test_pdf.py /data

echo "--- Running tests inside Docker container ---"
# We override the entrypoint to run the unittest module.
# The -v flag provides verbose output from the tests.
docker run --rm --entrypoint python3 -v "$TEST_PDF_DIR":/data -v "$(pwd)":/app pdf-ocr-cli -m unittest discover -v

echo "--- Test run finished ---"

# Clean up the temporary directory
rm -rf "$TEST_PDF_DIR"
