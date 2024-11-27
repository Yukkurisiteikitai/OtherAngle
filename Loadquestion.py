import csv

#本番環境
def LoadQuestion(loadpath):
    with open(loadpath,"r",encoding="utf-8") as file:
        question_list,theme_list = [],[]
        data = csv.reader(file)
        print(data)
        for q in data:
            question_list.append(q[0])
            theme_list.append(q[1])
    return question_list,theme_list

def makeQuestion(viewPoint:str,theme:str):
    #~というテーマについて~観点観点からアドバイスしてください
    return theme + "というテーマについて" + viewPoint + "観点からアドバイスしてください"