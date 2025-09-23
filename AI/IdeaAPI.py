import os
import time
import random
import json
import asyncio
import lm_studio_client

# ローカルモデル関連のライブラリをtry-exceptで囲む
try:
    import torch
    from transformers import AutoTokenizer
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
# streamer = TextIteratorStreamer(tokenizer=tokenizer,skip_prompt=True,skip_special_tokens=True)

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
    response = ""

    # まずローカルモデルでの推論を試みる
    if LOCAL_MODEL_AVAILABLE and model is not None and tokenizer is not None:
        print("ローカルモデルで推論を実行します...")
        try:
            prompt = tokenizer.apply_chat_template(
                conversation=conversation_history,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = tokenizer([prompt], return_tensors="pt", padding=True).to("cuda")
            with torch.cuda.amp.autocast():
                generated_ids = model.generate(
                    model_inputs.input_ids,
                    attention_mask=model_inputs.attention_mask,
                    max_new_tokens=500
                )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"ローカルモデルでの推論中にエラーが発生しました: {e}")
            response = "" # エラーが発生したらresponseを空にしておく

    # ローカルモデルでの推論が失敗した場合、LM Studioにフォールバック
    if not response:
        print("LM Studioにフォールバックして推論を実行します...")
        try:
            response = lm_studio_client.generate_text(conversation_history)
        except Exception as e:
            print(f"LM Studioでの推論中にエラーが発生しました: {e}")
            response = "エラー: 全ての推論方法に失敗しました。"


    # 会話履歴に回答を追加
    conversation_history.append({"role": "assistant", "content": response})
    end_time = time.time()
    print("実行時間: {:.2f}秒".format(end_time - start_time))
    # メモリキャッシュの解放
    # torch.cuda.empty_cache() # ローカルモデル使用時に移動済み
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
    user_input = input_user    
    Reset()

    conversation_history.append({"role": "user", "content": user_input})
    response = ""

    # まずローカルモデルでの推論を試みる
    if LOCAL_MODEL_AVAILABLE and model is not None and tokenizer is not None:
        print("ローカルモデルで推論を実行します...")
        try:
            prompt = tokenizer.apply_chat_template(
                conversation=conversation_history,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = tokenizer([prompt], return_tensors="pt", padding=True).to("cuda")
            with torch.cuda.amp.autocast():
                generated_ids = model.generate(
                    model_inputs.input_ids,
                    attention_mask=model_inputs.attention_mask,
                    max_new_tokens=10,
                    temperature=0.4,
                    top_p=0.7,
                    top_k=4
                )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"ローカルモデルでの推論中にエラーが発生しました: {e}")
            response = "" # エラーが発生したらresponseを空にしておく
    
    # ローカルモデルでの推論が失敗した場合、LM Studioにフォールバック
    if not response:
        print("LM Studioにフォールバックして推論を実行します...")
        try:
            response = lm_studio_client.generate_text(conversation_history)
        except Exception as e:
            print(f"LM Studioでの推論中にエラーが発生しました: {e}")
            response = "エラー: 全ての推論方法に失敗しました。"

    conversation_history.append({"role": "assistant", "content": response})
    
    response_temp = response
    save = AddSaveDataInfo(SystemPrompt,user_input,response_temp)
    save_data.append(str(save).replace("'",'"'))
    PromptSave()

    return response
    # return streamer

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