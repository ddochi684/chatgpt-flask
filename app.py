from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]  # 환경변수에서 API 키 불러오기

@app.route("/chat", methods=["POST"])
def chat():
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
