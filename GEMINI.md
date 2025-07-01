**プロジェクト名:** PDF OCR CLI Tool

**目的:**
ユーザーがコマンドラインからPDFファイルを指定し、その内容にTesseract OCRを適用し、抽出されたテキストと各単語の位置情報（バウンディングボックス）、信頼度をJSON形式で標準出力または指定されたファイルに出力する。このツールはDockerコンテナとして提供される。

**ターゲットユーザー:**
Python開発者、データアナリスト、CLIツール利用者、Docker利用者

**技術スタック:**

  * Python 3.9+
  * `argparse` (コマンドライン引数処理)
  * `PyMuPDF` (PDFから画像への変換)
  * `Pillow` (画像処理)
  * `PyTesseract` (Tesseract OCRエンジンのラッパー)
  * `pandas` (OCR結果のデータ処理、任意だが推奨)
  * `json` (JSON出力)

**外部依存ツール (Dockerコンテナ内に含める):**

  * **Tesseract OCRエンジン本体:** Dockerfile内でインストール。
  * **日本語言語データ (`jpn.traineddata`):** Dockerfile内でTesseractと共に導入。
  * **Poppler-utils (Linux):** `pdftocairo` や `pdftoppm` など。`PyMuPDF` が内部的にこれらを利用する場合があるため、Dockerfile内でインストールする（安定性向上）。

-----

### 生成AI向け仕様書

#### 1\. ツール名とファイル構成

  * **ツール名:** `pdf_ocr_cli` (Dockerコンテナ内で実行されるコマンド)
  * **ファイル構成:**
      * `pdf_ocr_tool.py`: Python CLIツールの本体スクリプト。
      * `Dockerfile`: Dockerイメージをビルドするための定義ファイル。
      * `requirements.txt`: Pythonの依存ライブラリを記述するファイル。

#### 2\. `requirements.txt` の内容

Pythonの依存ライブラリを以下の形式で記述する。

```
PyMuPDF # fitz
Pillow
pytesseract
pandas
```

#### 3\. `Dockerfile` の内容

以下の要件を満たす `Dockerfile` を作成すること。

  * **ベースイメージ:** `python:3.9-slim-buster` または同等の軽量なDebianベースのPythonイメージを使用する。
  * **システム依存関係のインストール:**
      * `apt-get update` 後、以下のパッケージをインストールする。
          * `tesseract-ocr` (Tesseract OCRエンジン本体)
          * `tesseract-ocr-jpn` (日本語言語データ)
          * `poppler-utils` (PDFレンダリングユーティリティ。`PyMuPDF` の安定性向上のため推奨)
          * `pkg-config`, `build-essential` (一部ライブラリのビルドに必要な場合があるため)
      * インストール後、`apt-get clean` および `/var/lib/apt/lists/*` の削除を行い、イメージサイズを削減する。
  * **作業ディレクトリの設定:** `/app` をコンテナ内の作業ディレクトリとする。
  * **Python依存関係のインストール:**
      * `requirements.txt` を `/app` にコピーし、`pip install --no-cache-dir -r requirements.txt` を実行する。
  * **アプリケーションコードのコピー:**
      * `pdf_ocr_tool.py` を `/app` にコピーする。
  * **Tesseractの環境変数設定 (オプションだが推奨):**
      * `ENV TESSDATA_PREFIX /usr/share/tesseract-ocr/4.00/tessdata` (Tesseractの言語データパス。バージョンによって異なる場合があるため、適切なパスを確認すること)
      * `ENV PATH="/usr/bin:${PATH}"` (TesseractがPATHに含まれていることを確認)
  * **実行可能コマンドの設定:**
      * `ENTRYPOINT ["python", "/app/pdf_ocr_tool.py"]` を使用し、Dockerコンテナのデフォルトコマンドとしてスクリプトを設定する。これにより、`docker run my_ocr_image <args>` のように直接引数を渡せるようになる。

#### 4\. `pdf_ocr_tool.py` の内容

前回の仕様書に記載した `pdf_ocr_tool.py` の内容とほぼ同じだが、以下の点を留意する。

  * **コマンドライン引数:** 以下の引数をサポートすること。

    | 引数名          | タイプ    | 必須 | デフォルト値 | 説明                                                                    |
    | :-------------- | :-------- | :--- | :----------- | :---------------------------------------------------------------------- |
    | `<PDF_FILE>`    | string    | はい | なし         | OCR処理を行うPDFファイルのパス。Dockerコンテナ内部のパスを指定する。    |
    | `-o`, `--output` | string    | いいえ | stdout       | 結果を書き込むJSONファイルのパス。省略した場合、標準出力にJSONが出力される。 |
    | `-l`, `--lang`   | string    | いいえ | `jpn`        | Tesseract OCRで使用する言語コード (例: `jpn`, `eng`)。                 |
    | `-d`, `--dpi`    | integer   | いいえ | `300`        | OCR処理を行う際の画像解像度（DPI）。                                     |

  * **処理フロー:**

    1.  **引数の解析:** `argparse` を使用して、コマンドライン引数をパースする。

    2.  **入力PDFの検証:**

          * `<PDF_FILE>` で指定されたパスのファイルが存在し、読み込み可能であることを確認する。**Dockerコンテナ内部のファイルパスとして解釈される**。

    3.  **PDFのページごとの処理:**

          * `PyMuPDF` を使用してPDFファイルを開き、各ページをイテレートする。
          * 各ページを、指定されたDPI (`--dpi`) でPIL Imageオブジェクトに変換する。
              * `page.get_pixmap(matrix=fitz.Matrix(DPI/72, DPI/72))` を使用する。

    4.  **OCR処理:**

          * `PyTesseract.image_to_data()` を使用し、指定された言語 (`--lang`) でOCRを実行する。
          * `output_type=pytesseract.Output.DATAFRAME` を使用する。

    5.  **データ抽出と整形:**

          * `level == 5`、`conf != -1`、`text` が有効な単語のみを抽出する。
          * 以下のJSON構造に整形する（`confidence`は小数点以下2桁、`bbox`は整数）。

        <!-- end list -->

        ```json
        [
          {
            "page_number": 1,
            "page_overall_text": "PDFページ全体のテキスト (改行区切り)",
            "words": [
              {
                "text": "認識された単語",
                "bbox": {
                  "left": 100,
                  "top": 200,
                  "width": 50,
                  "height": 20
                },
                "confidence": 98.75
              },
              // ...他の単語...
            ]
          },
          // ...次のページ...
        ]
        ```

          * `page_overall_text` フィールドは、各ページに対して `pytesseract.image_to_string()` を再度実行して取得する。

    6.  **JSON出力:**

          * `json` モジュールでJSON文字列に変換し (`ensure_ascii=False`, `indent=2`)、`--output` が指定されていればファイルに、そうでなければ標準出力に出力する。

  * **エラーハンドリング:**

      * Tesseract OCRエンジンの未検出 (`pytesseract.TesseractNotFoundError`)、PDFファイルの未検出/アクセス不可 (`FileNotFoundError` または `fitz.FileNotFoundError`)、無効なPDFファイル、その他の予期せぬエラーを適切に処理し、標準エラー出力に分かりやすいメッセージを出力し、非ゼロの終了コードで終了する。

#### 5\. Dockerでの使用方法 (ユーザー向け説明)

生成されるツールは、以下の手順で利用できることを想定する。

1.  **Dockerイメージのビルド:**

      * `Dockerfile` と `pdf_ocr_tool.py`、`requirements.txt` が同じディレクトリにある状態で、以下のコマンドを実行する。
        ```bash
        docker build -t pdf-ocr-cli .
        ```

2.  **OCR処理の実行:**

      * ホストOS上のPDFファイルをコンテナ内部にマウントして実行する。
      * **標準出力への出力例:**
        ```bash
        docker run --rm -v /path/to/your/local/pdfs:/mnt pdf-ocr-cli /mnt/input.pdf > output.json
        ```
          * `/path/to/your/local/pdfs` はホストOS上のPDFファイルがあるディレクトリのパス。
          * `/mnt` はコンテナ内部にマウントされるパス。
          * `input.pdf` はマウントされたディレクトリ内のPDFファイル名。
          * `output.json` はリダイレクトされるJSONファイル名。
      * **ファイルへの直接出力例 (推奨):**
        ```bash
        docker run --rm -v /path/to/your/local/pdfs:/mnt pdf-ocr-cli /mnt/input.pdf -o /mnt/output.json
        ```
          * この場合、`/mnt/output.json` はホストOS上の `/path/to/your/local/pdfs/output.json` として出力される。

#### 6\. テストケース (生成AIが内部的に確認するための参考)

  * 正常な日本語PDFファイル (`sample_jp.pdf`) を与えた場合、日本語テキストと正確な位置情報を含むJSONが出力されること。
  * 正常な英語PDFファイル (`sample_en.pdf`) を与え、`-l eng` を指定した場合、英語テキストと正確な位置情報を含むJSONが出力されること。
  * 存在しないPDFファイルパスを与えた場合、`FileNotFoundError` 系のエラーメッセージが出力され、非ゼロ終了すること。
  * 破損したPDFファイルを与えた場合、適切なエラーメッセージが出力され、非ゼロ終了すること。
  * `--output` オプションを指定した場合としない場合で、出力先が正しく切り替わること。
  * `--dpi` オプションで異なるDPIを指定した場合に処理が正しく行われること。

