from flask import Flask, request, jsonify, redirect
import openai
import os
import threading
from uuid import uuid4

app = Flask(__name__)

# 🔐 Render 환경변수에서 API 키 불러오기
openai.api_key = os.environ["OPENAI_API_KEY"]

# 💾 답변 저장용 (간단히 메모리에 저장)
answers = {}

# ✅ 루트 확인용
@app.route("/", methods=["GET"])
def index():
    return "GPT Chatbot is running!"

# ✅ 카카오 챗봇에서 질문 들어옴
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json['userRequest']['utterance']
    qid = str(uuid4())  # 질문 ID 생성
    answers[qid] = "답변을 준비 중입니다..."

    # ChatGPT 작업을 백그라운드로 실행
    threading.Thread(target=ask_chatgpt_and_save, args=(qid, user_input)).start()

    # 사용자에게 링크 전송
    link = f"https://chatgpt-flask-af1v.onrender.com/answer?id={qid}"
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": f"🤖 답변을 준비 중입니다!\n👇 아래 링크에서 확인해 주세요:\n{link}"
                }
            }]
        }
    })

# ✅ ChatGPT 응답 처리
def ask_chatgpt_and_save(qid, user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 공무원 복무 상담 챗봇이야."},
                {"role": "user", "content": user_input}
            ]
        )
        answers[qid] = response.choices[0].message.content
    except Exception as e:
        answers[qid] = f"⚠️ 오류 발생: {str(e)}"

# ✅ 사용자 링크 클릭 시 응답 출력
@app.route("/answer", methods=["GET"])
def answer():
    qid = request.args.get("id")
    result = answers.get(qid, "❗ 답변을 찾을 수 없습니다.")
    return f"""
        <html>
        <body style="font-family:sans-serif; padding:30px;">
            <h2>GPT 답변</h2>
            <p>{result}</p>
        </body>
        </html>
    """

# ✅ Render 포트 지정
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
