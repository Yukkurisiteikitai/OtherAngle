import os
import time
import random
import json
import asyncio
import lm_studio_client
from threading import Thread

# ローカルモデル関連のライブラリをtry-exceptで囲む
try:
    import torch
    from transformers import AutoTokenizer, TextIteratorStreamer
    from peft import AutoPeftModelForCausalLM
    LOCAL_MODEL_AVAILABLE = True
except ImportError:
    LOCAL_MODEL_AVAILABLE = False

import Loadquestion

# モデルとトークナイザーをNoneで初期化
model = None
tokenizer = None

# モデルの設定
adpt_path = "./BadMargeModel"
repo_id = "elyza/Llama-3-ELYZA-JP-8B"

# ローカルモデルが利用可能な場合のみ読み込みを試みる
if LOCAL_MODEL_AVAILABLE:
    print("ローカルモデルの読み込みを試みます...")
    try:
        model = AutoPeftModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=adpt_path,
            local_files_only=True,
            device_map="auto",
            torch_dtype=torch.float16,
            load_in_4bit=True
        )
        model.eval()
        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=repo_id)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        print("[Success]-Tokenizer-Model-Load")
    except Exception as e:
        print(f"ローカルモデルの読み込みに失敗しました: {e}")
        LOCAL_MODEL_AVAILABLE = False
else:
    print("Transformersライブラリが見つからないため、ローカルモデルは使用できません。")

# 質問の設定
QuestionCSVpath = "seePointANDtheme.csv"
seePoints, themes = Loadquestion.LoadQuestion(QuestionCSVpath)
conversation_history = []
SystemPrompt = "あなたは優秀なサポーターです。目的は一つのテーマを様々な観点から見ることでそのテーマを分析すること。そのテーマをその観点からみたらどうなるかを教えてください。ただし300文字程度に収めてください。"

#SaveDatas
save_data = []
save_path = "./testPrompts/Log.jsonl"

def AddSaveDataInfo(systemPrompt:str,qestion:str,answer:str):
    return    {
        "messages":[
            {'SystemPrompt':''+''+systemPrompt},
            {'question':qestion},
            {'answer':answer}
        ]
    }

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
    # This is the original non-streaming function, kept for compatibility
    user_input = Loadquestion.makeQuestion(seePoints[random.randint(0, len(seePoints) - 1)], theme)
    return Outputs_custom(user_input)

def Outputs_custom(input_user :str):
    # This is the original non-streaming function, kept for compatibility
    full_response = ""
    for chunk in Outputs_custom_stream(input_user):
        full_response += chunk
    return full_response

def Outputs_custom_stream(input_user: str):
    global save_data, SystemPrompt
    user_input = input_user
    Reset()

    conversation_history.append({"role": "user", "content": user_input})
    response_generated = False

    if LOCAL_MODEL_AVAILABLE and model is not None and tokenizer is not None:
        print("ローカルモデルでストリーミング推論を実行します...")
        try:
            streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
            prompt = tokenizer.apply_chat_template(
                conversation=conversation_history,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = tokenizer([prompt], return_tensors="pt", padding=True).to("cuda")
            
            generation_kwargs = dict(
                model_inputs,
                streamer=streamer,
                max_new_tokens=500,
                temperature=0.4,
                top_p=0.7,
                top_k=40,
            )
            
            thread = Thread(target=model.generate, kwargs=generation_kwargs)
            thread.start()
            response_generated = True
            
            full_response = ""
            for new_text in streamer:
                full_response += new_text
                yield new_text
            
            thread.join()
            torch.cuda.empty_cache()
            # Save the full response after streaming is complete
            save = AddSaveDataInfo(SystemPrompt, user_input, full_response)
            save_data.append(str(save).replace("'", '"'))
            PromptSave()

        except Exception as e:
            print(f"ローカルモデルでのストリーミング推論中にエラーが発生しました: {e}")
            response_generated = False

    if not response_generated:
        print("LM Studioにフォールバックしてストリーミング推論を実行します...")
        try:
            full_response = ""
            for chunk in lm_studio_client.generate_text_stream(conversation_history):
                full_response += chunk
                yield chunk
            
            # Save the full response after streaming is complete
            save = AddSaveDataInfo(SystemPrompt, user_input, full_response)
            save_data.append(str(save).replace("'", '"'))
            PromptSave()

        except Exception as e:
            print(f"LM Studioでのストリーミング推論中にエラーが発生しました: {e}")
            yield "エラー: 全ての推論方法に失敗しました。"

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
