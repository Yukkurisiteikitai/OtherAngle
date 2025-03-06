import os
import torch
from transformers import AutoTokenizer

# ,TextIteratorStreamer
from peft import AutoPeftModelForCausalLM
import time
import random
import Loadquestion
import json
# from timeout_decorator import timeout
import asyncio
from huggingface_hub import login
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()


#token
hf_token= os.getenv("hf_token")
login(hf_token)

# モデルの設定
adpt_path = "./BadMargeModel"
# repo_id = "elyza/Llama-3-ELYZA-JP-8B"
repo_id = "elyza/Llama-3-ELYZA-JP-8B"


# モデルの読み込み
try:
    model = AutoPeftModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=adpt_path,
        local_files_only=True,
        device_map="auto",  # 自動的にデバイスを割り当て
        torch_dtype=torch.float16,
        load_in_4bit=True  # 4bit量子化
    )
    model.eval()
except EOFError:
    print("failure-Model-Load")
try:
    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=repo_id,
                                              local_files_only=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
except EOFError:
    print("failure-Load-Tokenizer")

print("[Success]-Tokenizer-Model-Load")