import requests

# Gemini APIにリクエストを送るための関数
def get_gemini_response(user_message):
    api_url = "https://gemini-api-url.com/v1/chat"  # Gemini APIのURL
    headers = {
        "Authorization": "AIzaSyATinzFWGAMU2lX1sgNoh5PfXsbighBLXc"  # 必要に応じて認証情報を追加
    }
    payload = {
        "messages": [{"role": "user", "content": user_message}]  # ユーザーからのメッセージ
    }

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json().get("choices")[0].get("message").get("content")
    else:
        return "APIリクエストに失敗しました。"
    
   