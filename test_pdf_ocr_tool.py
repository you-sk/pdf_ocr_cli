
import unittest
import subprocess
import json
import os

class TestPdfOcrCli(unittest.TestCase):

    # All paths are relative to the container's /data directory for test PDFs
    TEST_JP_PDF = "/data/test_jp.pdf"
    TEST_EN_PDF = "/data/test_en.pdf"
    OUTPUT_JSON = "/data/test_output.json"

    def tearDown(self):
        """Clean up generated files after each test."""
        if os.path.exists(self.OUTPUT_JSON):
            os.remove(self.OUTPUT_JSON)

    def run_cli_command(self, args):
        """Helper function to run the CLI tool inside the container."""
        command = [
            "python3", "/app/pdf_ocr_tool.py"
        ] + args
        # We use check=False to allow tests for non-zero exit codes
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def test_japanese_ocr_stdout(self):
        """Test OCR on a Japanese PDF, outputting to stdout."""
        args = [self.TEST_JP_PDF, "--lang", "jpn"]
        result = self.run_cli_command(args)
        
        self.assertEqual(result.returncode, 0, f"CLI command failed with stderr: {result.stderr}")
        self.assertTrue(result.stdout, "Stdout should not be empty")
        
        try:
            data = json.loads(result.stdout)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            self.assertIn("日本語", data[0]["page_overall_text"])
        except json.JSONDecodeError:
            self.fail("Failed to decode JSON from stdout")

    def test_english_ocr_file_output(self):
        """Test OCR on an English PDF, outputting to a file."""
        args = [self.TEST_EN_PDF, "--lang", "eng", "-o", self.OUTPUT_JSON]
        result = self.run_cli_command(args)

        self.assertEqual(result.returncode, 0, f"CLI command failed with stderr: {result.stderr}")
        self.assertTrue(os.path.exists(self.OUTPUT_JSON), "Output file was not created")

        with open(self.OUTPUT_JSON, 'r') as f:
            data = json.load(f)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            self.assertIn("English", data[0]["page_overall_text"])

    def test_file_not_found(self):
        """Test the tool's behavior when the input PDF is not found."""
        args = ["non_existent_file.pdf"]
        result = self.run_cli_command(args)
        
        self.assertNotEqual(result.returncode, 0, "Command should fail for non-existent files")
        self.assertIn("Error: Input file not found", result.stderr)

    def test_psm_argument(self):
        """Test that the --psm argument is correctly handled."""
        args = [self.TEST_EN_PDF, "--lang", "eng", "--psm", "3"]
        result = self.run_cli_command(args)

        self.assertEqual(result.returncode, 0, f"CLI command failed with stderr: {result.stderr}")
        data = json.loads(result.stdout)
        self.assertIn("English", data[0]["page_overall_text"])

if __name__ == '__main__':
    unittest.main()
