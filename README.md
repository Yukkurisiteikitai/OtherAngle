# OtherAngle
複数の視点を提示し、1つのテーマを多角的に考えるためのサイト。

**推奨空き容量**
10GB以上（モデルダウンロードのため）

---

# 動作環境

| 項目     | version                 |
| ------ | ----------------------- |
| OS     | Windows 10 / Windows 11 |
| Python | 3.11.7                  |
| CUDA   | 12.4                    |
| GPU    | CUDA対応GPU               |

---

# セットアップ

### 1. ダウンロード

```bash
git clone https://github.com/Yukkurisiteikitai/OtherAngle.git
cd OtherAngle
```

### 2. HuggingFace アカウント作成

https://huggingface.co/

ログイン後、アクセストークンを取得。

### 3. `.env` 設定

```env
hf_token=YOUR_HUGGINGFACE_TOKEN
```

### 4. モデルインストール

```bat
start boot.bat
```

初回実行時に

* Python環境構築
* モデルダウンロード

が実行される。

---

# 実行

このシステムは **2つのサーバーで構成される**

```
AI Server
Web Server
```

## AIサーバー起動

```bat
start setup.bat
```

---

# 停止

```
Ctrl + C
```

---

# システム構成

```
Client
  │
  ▼
Web Server
  │
  ▼
AI Server (LLM推論)
```

---

# 主要ライブラリ

## AI推論

| ライブラリ        | 用途                |
| ------------ | ----------------- |
| torch        | CUDA対応ディープラーニング実行 |
| transformers | HuggingFaceモデル推論  |
| accelerate   | GPU / CPU 推論管理    |
| peft         | LoRAモデル対応         |

## APIサーバー

| ライブラリ    | 用途        |
| -------- | --------- |
| fastapi  | 高速APIサーバー |
| uvicorn  | ASGIサーバー  |
| pydantic | データ検証     |

## モデル管理

| ライブラリ           | 用途        |
| --------------- | --------- |
| huggingface-hub | モデルダウンロード |

## 補助

| ライブラリ         | 用途       |
| ------------- | -------- |
| tqdm          | 進捗表示     |
| psutil        | システム情報取得 |
| python-dotenv | 環境変数管理   |

---

# ライセンス

[MIT](./LICENSE)
