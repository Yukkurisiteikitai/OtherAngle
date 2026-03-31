import openai
import json
import os

def generate_text(conversation_history: list) -> str:
    """
    LM StudioのAPIを呼び出して、テキストを生成します。

    Args:
        conversation_history (list): OpenAI形式の会話履歴のリスト。

    Returns:
        str: モデルによって生成されたテキスト。
    """
    lm_studio_config_path = "lm_studio.json"
    
    if not os.path.exists(lm_studio_config_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {lm_studio_config_path}")

    with open(lm_studio_config_path, "r", encoding="utf-8") as f:
        lm_studio_config = json.load(f)

    client = openai.OpenAI(
        base_url=lm_studio_config.get("base_url"),
        api_key="lm-studio"  # LM StudioはAPIキー不要
    )

    try:
        completion = client.chat.completions.create(
            model=lm_studio_config.get("model"),
            messages=conversation_history,
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"LM Studioへのリクエスト中にエラーが発生しました: {e}")
        return "エラー: テキストを生成できませんでした。"

def generate_text_stream(conversation_history: list):
    """
    LM StudioのAPIを呼び出して、テキストをストリーミングで生成します。

    Args:
        conversation_history (list): OpenAI形式の会話履歴のリスト。

    Yields:
        str: モデルによって生成されたテキストのチャンク。
    """
    lm_studio_config_path = "lm_studio.json"
    
    if not os.path.exists(lm_studio_config_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {lm_studio_config_path}")

    with open(lm_studio_config_path, "r", encoding="utf-8") as f:
        lm_studio_config = json.load(f)

    client = openai.OpenAI(
        base_url=lm_studio_config.get("base_url"),
        api_key="lm-studio"
    )

    try:
        stream = client.chat.completions.create(
            model=lm_studio_config.get("model"),
            messages=conversation_history,
            temperature=0.7,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print(f"LM Studioへのストリーミングリクエスト中にエラーが発生しました: {e}")
        yield "エラー: テキストを生成できませんでした。"