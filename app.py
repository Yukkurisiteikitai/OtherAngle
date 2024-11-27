from flask import Flask, request, render_template, redirect,abort,Response
from urllib.parse import unquote
from flask_cors import CORS
import Loadquestion
import requests
import random
import IdeaAPI

app = Flask(__name__)
QuestionCSVpath = "seePointANDtheme.csv"
seePoints, themes = Loadquestion.LoadQuestion(QuestionCSVpath)


CORS(app, resources={r"/*": {
    "origins": ["http://127.0.0.1:8030", "https://example.com","http://127.0.0.1:8000"],
    "methods": ["GET", "POST"],
    "allow_headers": [r"*"]
}})



def viewPointMake(theme:str ,content:str):
    # app.make
    return (theme,content)

        

reset = ""

#setPrameter
content_dict = {
        'content1':reset,
        'content2':reset,
        'content3':reset,
        'view1':reset,
        'view2':reset,
        'view3':reset,
    }
theme_input="テーマを入力してください"

def generate(theme):
    viewPoint = seePoints[random.randint(0, len(seePoints) - 1)]
    promptInput = Loadquestion.makeQuestion(viewPoint, theme)
    print(promptInput)
    return IdeaAPI.Outputs_custom(promptInput),viewPoint


@app.route("/")
def site_start():
    global content_dict,theme_input
    #非効率だけど全部それぞれ適用する方法
    content_dict = {
        'content1':reset,
        'content2':reset,
        'content3':reset,
        'view1':reset,
        'view2':reset,
        'view3':reset,
    }
    return render_template("index.html",content_dict=content_dict,
                           theme_input="テーマを入力してください")


@app.route("/request/<theme>")
def suiron_request(theme:str):
    return f"NOW_LOAD{theme}"



@app.route("/test")
def hihluhnoi():
    global theme_temp
    #取得
    theme_value = request.args.get('a')

    content_value = request.args.get('c')

    if len(content_value) > 40:
        return {"ERROR":"OverThemeWords","code":len(content_value)}
    
    return {"test":"clear","valuse":len(content_value)}


#apiにtypeとcontentをリクエストする.
def request_api(type:str,content:str):
    url = "http://127.0.0.1:8030"
    url += "/inference/type/" + type
    url += "?c=" + content
    response = requests.get(url)
    response.raise_for_status()
    return response.json()



#フォームの取得する部分.
theme_temp =""
@app.route("/setForm")
def setForm():
    # print("set")
    theme_input = request.args.get('theme')
    theme_temp=theme_input



    theme_count = len(theme_temp)
    print(theme_count)
    if theme_count > 40:
        return {"ERROR":"OverThemeWords"}
    
    url = "/req?t=theme&c=" + theme_input
    return redirect(url)

@app.route("/promptTest")
def promptTest():
    theme = ""
    seePoints = ""
    return {"theme":theme,
            "seePoints":seePoints}



@app.route("/generate")
def generate_stream():
    """
    クライアントからプロンプトを受け取り、AIの出力をストリーミングで返す
    """
    # クライアントからプロンプトを取得
    prompt = request.json.get('prompt')


    # ストリーミングでAIの応答を返す関数
    def generate_ai_response():
        # AI処理を実行
        streamer = IdeaAPI.Outputs_custom(theme=theme_input)
        
        # ストリームでAIの応答を1トークンずつ送信
        for token in streamer:
            yield token + "\n"  # トークンをストリームで送信
        
    # レスポンスとしてストリーミングを返す
    return Response(generate_ai_response(), content_type='text/plain;charset=utf-8')



#フォームの入力を実際にリクエストするところ.
# @app.route("/req")
# def noi():
#     global content_dict
#     #取得
#     theme_value = request.args.get('t')

#     content_value = request.args.get('c')


#     # URLデコードを行う
#     content_value = unquote(content_value)

#     if len(content_value) > 40:
#         # エラーの場合は処理を中断し、エラーレスポンスを返す
#         return abort(400, f"Content too long: {len(content_value)} characters")


#     answers = ["","",""]
#     viewPoint = ["","",""]
    

#     for i in range(3):
#         req = request_api(type=theme_value,content=content_value)
#         app.logger.info('%s request', req)


#         answers[i](req['content'])
#         viewPoint[i](req['viewPoint'])
#         app.logger.info('%s viewPoint', viewPoint[i])
#         app.logger.info('%s answers', answers[i])

#     content_dict = {
#         'content1':answers[0],
#         'content2':answers[1],
#         'content3':answers[2],
#         'view1':viewPoint[0],
#         'view2':viewPoint[1],
#         'view3':viewPoint[2],
#     }


#     return render_template("index.html",content_dict=content_dict,theme_input=content_value)()

#アプリ実行
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8120, debug=False)