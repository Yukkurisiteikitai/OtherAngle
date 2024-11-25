import csv

#テスト環境
def LoadTestQ(loadcsvPath):
    with open(loadcsvPath,"r",encoding="utf-8") as file:
        data = csv.reader(file)
        print(data)
        question_list = [q[0] for q in data]
        theme_list = [q[1] for q in data]
    return question_list,theme_list

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

def makeQuestion(question:str,theme:str):
    #~というテーマについて~観点観点からアドバイスしてください
    return theme + "というテーマについて" + question + "観点からアドバイスしてください"

# q = []
# b = []

# # q,b = LoadQuestion("seePointANDtheme.csv")
# # # q,b = LoadTestQ("seePointANDtheme.csv")

# # print("-----question-------")
# # print(q)
# # print("-----theme-------")
# # print(b)