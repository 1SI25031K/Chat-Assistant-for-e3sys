FROM python:3.12-slim

# バッファリングを無効化
ENV PYTHONUNBUFFERED=1
# pycacheを作らない
ENV PYTHONDONTWRITEBYTECODE=1

# 3. 作業ディレクトリの設定
WORKDIR /app

# 4. 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY . .

# 起動
CMD ["python", "backend/main.py"]
