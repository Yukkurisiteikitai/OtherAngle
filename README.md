
# 概要
複数の視点を提供し、多角的に物事を見るためのサイトのリポジトリです。
推奨空き容量:10GB以上

# 想定環境
windows11
windows10
cuda:12.7



# インストール
1. githubからリポジトリをインストール  
`git clone https://github.com/Yukkurisiteikitai/OtherAngle.git`
2. huggingFaceの登録/Loginをする
3. huggingFaceのアクセストークンを.envのhf_tokenに入れる
4. モデルのインストールと環境構築を行います  
`start boot.bat`  


# 実行方法
AIのサーバーとサイトのサーバーで構成されています

## AIのサーバーの起動手順
実行
```
start setup.bat
```

# 終了手順
Control + Cで強制終了する



### 実行環境
windows11
Python 3.11.7
cuda release 12.4, V12.4.99

### 使用ライブラリ
accelerate==1.1.1
annotated-types==0.7.0
bitsandbytes==0.44.1
fastapi==0.115.5
fastapi-cli==0.0.5
httpcore==1.0.7
httptools==0.6.4
httpx==0.27.2
huggingface-hub==0.26.2
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.3
markdown-it-py==3.0.0
MarkupSafe==2.1.5
mdurl==0.1.2
mpmath==1.3.0
networkx==3.2.1
numpy==1.26.3
orjson==3.10.12
packaging==24.2
peft==0.13.2
psutil==6.1.0
pydantic==2.10.1
pydantic-extra-types==2.10.0
pydantic-settings==2.6.1
pydantic_core==2.27.1
Pygments==2.18.0
python-dotenv==1.0.1
python-multipart==0.0.17
PyYAML==6.0.2
regex==2024.11.6
requests==2.32.3
safetensors==0.4.5
shellingham==1.5.4
sniffio==1.3.1
starlette==0.41.3
sympy==1.13.1
timeout-decorator==0.5.0
tokenizers==0.20.3
torch==2.5.1+cu124
torchaudio==2.5.1+cu124
torchvision==0.20.1+cu124
tqdm==4.67.0
transformers==4.46.2
typer==0.13.1
typing_extensions==4.12.2
ujson==5.10.0
urllib3==2.2.3
uvicorn==0.32.1
