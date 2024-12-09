from flask import Flask, request, render_template, redirect,abort
from urllib.parse import unquote
from flask_cors import CORS
import requests

app = Flask(__name__)

# frontend site=>http://127.0.0.1:8030
CORS(app, resources={r"/*": {
    "origins": ["http://127.0.0.1:8030", "https://example.com","http://127.0.0.1:8000"],
    "methods": ["GET", "POST"],
    "allow_headers": [r"*"]
}})


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


def reset_do():
    global content_dict,theme_input
    content_dict = {
        'content1': reset,
        'content2': reset,
        'content3': reset,
        'view1': reset,
        'view2': reset,
        'view3': reset,
    }
    theme_input = "テーマを入力してください"


@app.route("/")
def site_start():
    global content_dict,theme_input
    reset_do()
    return render_template("index.html",content_dict=content_dict,
                           theme_input=theme_input)


@app.route("/request/<theme>")
def suiron_request(theme:str):
    return f"NOW_LOAD{theme}"



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

    if len(theme_temp) > 40:
        return {"ERROR":"OverThemeWords"}

    url = "/req?t=theme&c=" + theme_input
    return redirect(url)




#フォームの入力を実際にリクエストするところ.
@app.route("/req")
def get_inference():
    #取得
    theme_value = request.args.get('t')
    content_value = request.args.get('c')

    # URLデコードを行う
    content_value = unquote(content_value)

    if len(content_value) > 40:
        # エラーの場合は処理を中断し、エラーレスポンスを返す
        return abort(400, f"Content too long: {len(content_value)} characters")


    answers = ["","",""]
    viewPoint = ["","",""]


    for i in range(3):
        req_api = request_api(type=theme_value,content=content_value)

        answers[i] = str(req_api['answers'])
        viewPoint[i] = str(req_api['viewPoint'])

    content_dict = {
        'content1':answers[0],
        'content2':answers[1],
        'content3':answers[2],
        'view1':viewPoint[0],
        'view2':viewPoint[1],
        'view3':viewPoint[2],
    }


    return render_template("index.html",content_dict=content_dict,theme_input=content_value)

#アプリ実行
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8120, debug=False)
