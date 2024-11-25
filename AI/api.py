import IdeaAPI
#custom
import Loadquestion
import random
import time



QuestionCSVpath = "seePointANDtheme.csv"
seePoints, themes = Loadquestion.LoadQuestion(QuestionCSVpath)
countsSameTheme=3

def rd(max):
    return random.randint(0,max)
def generate(theme):
    viewPoint = seePoints[random.randint(0, len(seePoints) - 1)]
    promptInput = Loadquestion.makeQuestion(viewPoint, theme)
    print(promptInput)
    return IdeaAPI.Outputs_custom(promptInput),viewPoint
import csv
def LoadCSV(path):
# print(sysPrompt)
    with open(path,"r",encoding="utf-8")as file:
        data = csv.reader(file)
        data_Firsts = []
        for i in data:
            data_Firsts.append(str(i[0]))
        return data_Firsts


Mode = ["custom","Auto"]

q = ["ファントムセンス",
     "AIは最高に優秀なスキルを持った人間のまがい物であるか",
     "この世の問題すべてに適応できない法則は何か?"]

# SetMode =""
# while True:
#     SetMode = input('Choice To Mode[custom/Auto]:')
#     if SetMode == Mode[0] or SetMode == "c" or SetMode == "" or SetMode == Mode[1] or SetMode == "a":
#         break





# if SetMode == Mode[0] or SetMode == "c" or SetMode == "":
# #手動テストモー:ド
#     while True:
#         IdeaAPI.Reset()
#         theme = input("theme:")
#         # theme = themes[rd(len(themes)-1)]
        
#         if theme == "exit" or theme == "":
#             IdeaAPI.PromptSave()
#             break
#         elif theme == "systemPrompt" or theme=="sp":
#             IdeaAPI.SetSystemPrompt()
#             theme = input("theme:")
#         elif theme == "savePrompt" or theme=="save":
#             IdeaAPI.PromptSave()
#             theme = input("theme:")
        
#         # print("回答",IdeaAPI.Outputs(theme))
        
#         for i in range(countsSameTheme):
#             s_t = time.time()
#             print(generate(theme))
#             e_t = time.time()
#             print("time:{:.2f}".format(e_t-s_t))

from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
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
    "http://192.168.1.17:8120"
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

log_path="log/log.csv"
class logData():
    def __init__(self) -> None:    
        # startSet
        data_number = []
        data_string = []

        #setting Datas
        LogLevel = 0
        time_log = time.time()
        eventID_log = 39
        RequestID_log = 2
        UserCode_log = 809458403 #ipアドレス or UserName
        DoPoint_log = "fe"
        ProcessingDetail_log = "feafae"
        ProcessingResult_log = "fejoifaw;fj"
        message_log = "message"

        # data {
        #     "LogLeven":LogLevel,
        #     "time":time_log,
        #     "eventID":eventID_log,
        #     "RequestID":RequestID_log,
        #     "UserCode":UserCode_log,
        #     "DoPoint":DoPoint_log,
        #     "ProcessingDetail":ProcessingDetail_log,
        #     "ProcessingResult":ProcessingResult_log,
        #     "message":message_log
        # }

        
        data_number.append(LogLevel)
        data_number.append(RequestID_log)
        data_number.append(eventID_log)
        data_number.append(UserCode_log)

        data_string.append(DoPoint_log)
        data_string.append(ProcessingDetail_log)
        data_string.append(ProcessingResult_log)
        data_string.append(message_log)



def save_log(data):
    with open(log_path,"a",encoding="utf-8")as f:
        writer = csv.DictWriter(f, data, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

#toDo  
@app.get("/hello")
async def hello():
    return {"content":"helloWorld"}

@app.get("/unluck")
async def unluck():
    return {"ERROR":"unluck"}

#クラス名を取得してから認識する


# seePoints = []
# import csv
# with open("seePoints.csv","r",encoding="utf-8")as f:
#     data = csv.reader(f)
#     seePoints=[i for i in data]
    

print(seePoints[2][0])


#api出力
@app.get("/inference/type/{type_value}")
def read_item(type_value: str, c: Union[str, None] = None):
    if type_value == "theme":
        # return {"content":generate(c)}
        content,viewP = generate(c)
        return {"type":"theme","theme":c,"viewPoint":viewP,"content":content}
    
    elif type_value == "unmodified":
        return {"type":"unmodified","content":c,"viewPoint":seePoints[random.randint(0,len(seePoints)-1)][0]}
    
    elif type_value == "test":
        return {"theme": type_value, "q": c}
    
    else:
        return {"ERROR":"NotFound"}