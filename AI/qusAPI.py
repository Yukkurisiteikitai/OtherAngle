from fastapi import FastAPI
import Loadquestion
import random

app = FastAPI()

seePoint = []
themes = []
seePoint,themes = Loadquestion.LoadQuestion("seePointANDtheme.csv")

def rd(list:list):
    return list[random.randint(0,len(list)-1)]

@app.get("/getData")
def getData():
    return rd(seePoint)