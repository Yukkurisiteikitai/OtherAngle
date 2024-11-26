import os
import torch
from transformers import AutoTokenizer,TextIteratorStreamer
from peft import AutoPeftModelForCausalLM
import time
import random
import Loadquestion
import json
from timeout_decorator import timeout

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
            max_new_tokens=500
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
def Outputs_custom(input_user :str):
    global save_data,SystemPrompt
    # print(f"SystemPrompt{SystemPrompt}")#test
    user_input = input_user    
    Reset()

    conversation_history.append({"role": "user", "content": user_input})
    prompt = tokenizer.apply_chat_template(
        conversation=conversation_history,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([prompt], return_tensors="pt", padding=True).to("cuda")
    with torch.cuda.amp.autocast():  # 混合精度を使用してメモリを節約
        generated_ids = model.generate(
            model_inputs.input_ids,
            attention_mask=model_inputs.attention_mask,
            max_new_tokens=500,
            streamer=streamer,
            temperature=0.4,
            top_p=0.7,
            top_k=4
        )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    conversation_history.append({"role": "assistant", "content": response})
    torch.cuda.empty_cache()
    # print(type(response))
    response_temp = ""
    response_temp = response
    # print(response_temp)#test
    # save_data.append(AddSaveDataInfo(SystemPrompt,user_input,response_temp))
    save = AddSaveDataInfo(SystemPrompt,user_input,response_temp)
    # save_data.append(AddSaveDataInfo(SystemPrompt,user_input,response_temp))
    save_data.append(str(save).replace("'",'"'))
    PromptSave()

    return response

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