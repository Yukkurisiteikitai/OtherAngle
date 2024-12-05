import os
import torch
from transformers import AutoTokenizer,TextIteratorStreamer
from peft import AutoPeftModelForCausalLM
import time
import random
import Loadquestion
import json
# from timeout_decorator import timeout
import asyncio
from typing import Union

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
    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=repo_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
except EOFError:
    print("failure-Load-Tokenizer")

print("[Success]-Tokenizer-Model-Load")

# 質問の設定
QuestionCSVpath = "seePointANDtheme.csv"
seePoints, themes = Loadquestion.LoadQuestion(QuestionCSVpath)
conversation_history = []
# SystemPrompt = "あなたは問題点を指摘するのが得意なアドバイザーです。今回は箇条書きで回答アドバイスしてください。また箇条書きは3つまでとなります。"
SystemPrompt = "あなたは優秀なサポーターです。目的は一つのテーマを様々な観点から見ることでそのテーマを分析すること。そのテーマをその観点からみたらどうなるかを教えてください。ただし300文字程度に収めてください。"

#SaveDatas
save_data = []
# save_path = "./testPrompts/RecToPrompts.jsonl"
save_path = "./testPrompts/Log.jsonl"

def AddSaveDataInfo(systemPrompt:str,qestion:str,answer:str):
    # return    {
    #     "messages":[
    #         {'"SystemPrompt"'+':"'+systemPrompt+'"'},
    #         {"question"+':"'+qestion+'"'},
    #         {'"answer"'+':"'+answer+'"'}
    #     ]
    # }
    # return    {
    #     "messages":[
    #         {"SystemPrompt"+":"+systemPrompt},
    #         {"question"+":"+qestion},
    #         {"answer"+":"+answer}
    #     ]
    # }
    return    {
        "messages":[
            {'SystemPrompt":"'+''+systemPrompt},
            {'question":"'+qestion},
            {'answer":"'+answer}
        ]
    }
streamer = TextIteratorStreamer(tokenizer=tokenizer,skip_prompt=True,skip_special_tokens=True)

def Reset():
    conversation_history = []
    conversation_history.append({"role": "user", "content": SystemPrompt})

def SetSystemPrompt():
    global SystemPrompt
    conversation_history = []
    SystemPrompt = input("SystemPrompt:")
    conversation_history.append({"role": "user", "content": SystemPrompt})
def ProgramSetSystemPrompt(prompt):
    global SystemPrompt
    conversation_history = []
    SystemPrompt = prompt
    conversation_history.append({"role": "system", "content": SystemPrompt})


Reset()

def Outputs(theme :str):
    # ランダムに質問を生成
    user_input = Loadquestion.makeQuestion(seePoints[random.randint(0, len(seePoints) - 1)], theme)    

    start_time = time.time()
    conversation_history.append({"role": "user", "content": user_input})

    # プロンプトの生成
    prompt = tokenizer.apply_chat_template(
        conversation=conversation_history,
        tokenize=False,
        add_generation_prompt=True
    )
    # 入力データの生成
    model_inputs = tokenizer([prompt], return_tensors="pt", padding=True).to("cuda")

    with torch.cuda.amp.autocast():  # 混合精度を使用してメモリを節約
        generated_ids = model.generate(
            model_inputs.input_ids,
            attention_mask=model_inputs.attention_mask,
            max_new_tokens=300
        )

    # 生成された回答を取得
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    # トークンIDを文字列に変換
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # 会話履歴に回答を追加
    conversation_history.append({"role": "assistant", "content": response})
    end_time = time.time()
    print("実行時間: {:.2f}秒".format(end_time - start_time))
    # メモリキャッシュの解放
    torch.cuda.empty_cache()
    response_temp = r""
    response_temp = response
    save = AddSaveDataInfo(SystemPrompt,user_input,response_temp)
    # save_data.append(AddSaveDataInfo(SystemPrompt,user_input,response_temp))
    save_data.append(str(save).replace("'",'"'))
    return response

# opt_minite = 3
# @timeout(60*opt_minite)



#    ~===============api==============
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Union
import random
import csv
import time

app = FastAPI()

origins = [
    "http://localhost:8000",
    "127.0.0.1",
    "http://127.0.0.1/",
    "http://10.16.100.132/",
    "http://10.16.100.132/",
    "http://10.16.100.132:8120",
    "http://192.168.1.17:8120",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def add_procss_time_header(request: Request,call_net):
    response = await call_net(request)
    print(response)
    return response




@app.get("/inference/type/{type_value}")
async def read_item(type_value: str, c: Union[str, None] = None, v: Union[str, None] = None):
    global conversation_history
    Reset()

    # 入力生成
    user_input = Loadquestion.makeQuestion(v, c)
    conversation_history.append({"role": "user", "content": user_input})

    # プロンプト作成
    prompt = tokenizer.apply_chat_template(
        conversation=conversation_history,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([prompt], return_tensors="pt", padding=True).to("cuda")

    # ストリーマーを再生成
    streamer = TextIteratorStreamer(
        tokenizer=tokenizer,
        skip_prompt=True,
        skip_special_tokens=True
    )

    async def generate_text():
        print("Starting model generation...")
        # モデルの生成を開始（非同期ストリーム処理）
        with torch.cuda.amp.autocast():
            model.generate(
                model_inputs.input_ids,
                attention_mask=model_inputs.attention_mask,
                max_new_tokens=500,
                streamer=streamer,
                temperature=0.4,
                top_p=0.7,
                top_k=4
            )
        print("Model generation completed.")

        for output in streamer:
            yield output


    # ストリーミングレスポンスを返す
    return StreamingResponse(generate_text(), media_type="text/plain")


import threading
# グローバル変数
conversation_history = []

# モデル推論を別スレッドで実行
def generate_model_output(model_inputs, streamer):
    with torch.no_grad():
        model.generate(
            model_inputs.input_ids,
            attention_mask=model_inputs.attention_mask,
            max_new_tokens=500,
            streamer=streamer,
            temperature=0.4,
            top_p=0.7,
            top_k=4
        )

@app.post("/generate")
async def generate_stream(request: Request):
    global conversation_history

    req_data = await request.json()
    user_input = req_data.get("prompt", "")
    if not user_input:
        return {"error": "Prompt is missing."}

    # 会話履歴にユーザー入力を追加
    conversation_history.append({"role": "user", "content": user_input})

    prompt = tokenizer.apply_chat_template(
        conversation=conversation_history,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([prompt], return_tensors="pt", padding=True).to("cuda")
    
    streamer = TextIteratorStreamer(tokenizer=tokenizer, skip_special_tokens=True)

    # モデル推論を別スレッドで実行
    thread = threading.Thread(target=generate_model_output, args=(model_inputs, streamer))
    thread.start()

    # ストリーミングレスポンスを返す
    async def stream_output():
        # ストリームから逐次トークンを取得して返す
        for output in streamer:
            yield output

    return StreamingResponse(stream_output(), media_type="text/plain")



# print(Outputs_custom("jfweioというテーマについて客観的観点からアドバイスしてください"))
save_path = "./testPrompts/giron.jsonl"
def PromptSave():
    global save_data,save_path
    if save_data == []:
        print("[NotingSaveData]")
    else:
        with open(save_path,"a",encoding="utf8")as file:
            file.writelines(f"{line}\n" for line in save_data)
        print("[Success Save]")
        save_data = []
    # save_data = []

# print("回答を終了させていただきました")