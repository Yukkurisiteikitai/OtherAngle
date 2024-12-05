import IdeaAPI
#custom
import Loadquestion
import random
import time
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Union
import random
import csv
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


# saberSet
app = FastAPI()

origins = [
    "http://localhost:8000",
    "127.0.0.1",
    "http://127.0.0.1/",
    "http://10.16.100.132/",
    "http://10.16.100.132/",
    "http://10.16.100.132:8120",
    "http://192.168.1.17:8120",
    "http://127.0.0.1:5500/"
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

#LogDatabase todo AWSにログを送信ように変更
class logData():
    # startSet
    data_number = []
    data_string = []

    #setting Datas
    LogLevel = 0
    time_log = time.time()
    eventID_log = 39
    RequestID_log = 2
    UserCode_log = 45323412 #ipアドレス or UserName
    DoPoint_log = ""
    ProcessingDetail_log = ""
    ProcessingResult_log = ""
    message_log = ""


    def __init__(self,LogLevel,time_log,eventID_log,RequestID_log,UserCode_log,DoPoint_log,ProcessingDetail_log,ProcessingResult_log,message_log,data_number,data_string):    
        data_number.append(LogLevel)
        data_number.append(RequestID_log)
        data_number.append(eventID_log)
        data_number.append(UserCode_log)

        data_string.append(DoPoint_log)
        data_string.append(ProcessingDetail_log)
        data_string.append(ProcessingResult_log)
        data_string.append(message_log)

    def setData(self,LogLevel,time_log,eventID_log,RequestID_log,UserCode_log,DoPoint_log,ProcessingDetail_log,ProcessingResult_log,message_log,data_number,data_string):
        return {
            "LogLevel":LogLevel,
            "time_log":time_log,
            "eventID_log":eventID_log,
            "RequestID_log":RequestID_log,
            "UserCode_log":UserCode_log,
            "DoPoint_log":DoPoint_log,
            "ProcessingDetail_log":ProcessingDetail_log,
            "ProcessingResult_log":ProcessingResult_log,
            "message_log":message_log
        }

    
def save_log(data):
    with open(log_path,"a",encoding="utf-8")as f:
        writer = csv.DictWriter(f, data, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)


# toDo  
@app.get("/hello")
async def hello():
    return {"content":"helloWorld"}


@app.get("/unluck")
async def unluck():
    return {"ERROR":"unluck"}



# api出力
@app.get("/inference/type/{type_value}")
def read_item(type_value: str, c: Union[str, None] = None,v: Union[str, None] = None):
    if type_value == "theme":
            promptInput = Loadquestion.makeQuestion(v, c)
            return StreamingResponse(IdeaAPI.Outputs_custom(promptInput))


    # 例外処理
    else:
        return {"ERROR":"NotFound"}