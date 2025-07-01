# PDF OCR CLI Tool

## 概要

このツールは、コマンドラインからPDFファイルを指定し、その内容にTesseract OCRを適用し、抽出されたテキストと各単語の位置情報（バウンディングボックス）、信頼度をJSON形式で標準出力または指定されたファイルに出力するCLIツールです。Dockerコンテナとして提供されるため、環境構築の手間なく利用できます。

### ターゲットユーザー

Python開発者、データアナリスト、CLIツール利用者、Docker利用者

## 機能

*   PDFファイルからのテキスト抽出と単語ごとの詳細情報（位置、信頼度）の取得。
*   Tesseract OCRエンジンの言語指定（日本語、英語など）。
*   OCR処理時の画像解像度（DPI）の指定。
*   Tesseractのページセグメンテーションモード（PSM）の指定。
*   画像の前処理（グレースケール化、二値化、罫線除去）によるOCR精度の向上。
*   結果をJSON形式で標準出力またはファイルに出力。

## 技術スタック

*   Python 3.9+
*   `argparse` (コマンドライン引数処理)
*   `PyMuPDF` (PDFから画像への変換)
*   `Pillow` (画像処理)
*   `PyTesseract` (Tesseract OCRエンジンのラッパー)
*   `pandas` (OCR結果のデータ処理)
*   `json` (JSON出力)
*   `opencv-python` (画像前処理)
*   `numpy` (画像前処理)

### 外部依存ツール (Dockerコンテナ内に含める)

*   **Tesseract OCRエンジン本体**
*   **日本語言語データ (`jpn.traineddata`)**
*   **Poppler-utils** (`PyMuPDF`の安定性向上のため)
*   **IPAフォント** (日本語PDF生成・表示のため)

## 使い方

### 1. Dockerイメージのビルド

`Dockerfile`、`pdf_ocr_tool.py`、`requirements.txt`、`create_test_pdf.py`、`test_pdf_ocr_tool.py`、`run_tests.sh` が同じディレクトリにある状態で、以下のコマンドを実行します。

```bash
docker build -t pdf-ocr-cli .
```

### 2. OCR処理の実行

ホストOS上のPDFファイルをコンテナ内部にマウントして実行します。

*   **標準出力への出力例:**
    ```bash
    docker run --rm -v /path/to/your/local/pdfs:/mnt pdf-ocr-cli /mnt/input.pdf > output.json
    ```
    *   `/path/to/your/local/pdfs` はホストOS上のPDFファイルがあるディレクトリのパス。
    *   `/mnt` はコンテナ内部にマウントされるパス。
    *   `input.pdf` はマウントされたディレクトリ内のPDFファイル名。
    *   `output.json` はリダイレクトされるJSONファイル名。

*   **ファイルへの直接出力例 (推奨):**
    ```bash
    docker run --rm -v /path/to/your/local/pdfs:/mnt pdf-ocr-cli /mnt/input.pdf -o /mnt/output.json
    ```
    *   この場合、`/mnt/output.json` はホストOS上の `/path/to/your/local/pdfs/output.json` として出力されます。

#### コマンドライン引数

| 引数名          | タイプ    | 必須 | デフォルト値 | 説明                                                                    |
| :-------------- | :-------- | :--- | :----------- | :---------------------------------------------------------------------- |
| `<PDF_FILE>`    | string    | はい | なし         | OCR処理を行うPDFファイルのパス。Dockerコンテナ内部のパスを指定する。    |
| `-o`, `--output` | string    | いいえ | stdout       | 結果を書き込むJSONファイルのパス。省略した場合、標準出力にJSONが出力される。 |
| `-l`, `--lang`   | string    | いいえ | `jpn`        | Tesseract OCRで使用する言語コード (例: `jpn`, `eng`)。                 |
| `-d`, `--dpi`    | integer   | いいえ | `300`        | OCR処理を行う際の画像解像度（DPI）。                                     |
| `--psm`          | integer   | いいえ | `6`          | Tesseract Page Segmentation Mode (PSM) selection.                      |

## テスト方法

本ツールには、Dockerコンテナ内で実行可能な統合テストが付属しています。

1.  **テストPDFの生成とテストの実行スクリプトに実行権限を付与します。**
    ```bash
    chmod +x run_tests.sh
    ```

2.  **以下のコマンドを実行して、テストを実行します。**
    ```bash
    ./run_tests.sh
    ```
    このスクリプトは、Dockerイメージのビルド、テスト用のPDFファイルの生成、そしてコンテナ内でのテストの実行を自動的に行います。

## ライセンス

このプロジェクトはMIT Licenseの下で公開されています。詳細については、`LICENSE`ファイルを参照してください。

---

**MIT License**

Copyright (c) 2025 [あなたの名前または組織名]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
