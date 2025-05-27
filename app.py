from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]  # 환경변수에서 API 키 가져오기

@app.route("/", methods=["GET"])
def index():
    return "GPT Chatbot is running!"

@app.route("/chat", methods=["POST"])
def chat():
    # ✅ 요청 확인용 로그 출력
    print("✅ /chat 요청 들어옴:", request.json)

    user_input = request.json['userRequest']['utterance']

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 공무원 복무 상담 챗봇이야."},
            {"role": "user", "content": user_input}
        ]
    )

    answer = response.choices[0].message.content

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": answer
                }
            }]
        }
    })

# ✅ Render에서 동작하도록 포트 설정
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
