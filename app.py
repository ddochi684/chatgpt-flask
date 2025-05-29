from flask import Flask, request, jsonify, redirect
import openai
import os
import threading
from uuid import uuid4

app = Flask(__name__)

# 🔐 Render 환경변수에서 API 키 불러오기
openai.api_key = os.environ["OPENAI_API_KEY"]

# 💾 질문 ID별 GPT 답변을 저장할 메모리 공간 (임시)
answers = {}

# ✅ 루트 확인용
@app.route("/", methods=["GET"])
def index():
    return "GPT Chatbot is running!"

# ✅ 카카오챗봇이 질문을 보낼 때 사용하는 엔드포인트
@app.route("/chat", methods=["POST"])
def chat():
    try:
        # 카카오에서 보낸 JSON 데이터 받기
        data = request.json
        print("✅ 카카오 요청 수신:", data)

        # 사용자의 질문 꺼내기 (안전하게 꺼냄)
        user_input = data.get('userRequest', {}).get('utterance', '')
        if not user_input:
            raise ValueError("❗ 사용자 발화(utterance)가 없습니다.")

        # 고유한 질문 ID 생성
        qid = str(uuid4())
        answers[qid] = "답변을 준비 중입니다..."

        # 백그라운드로 ChatGPT 호출 시작
        threading.Thread(target=ask_chatgpt_and_save, args=(qid, user_input)).start()

        # 사용자에게 답변 링크 제공
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

    except Exception as e:
        print(f"❗ 예외 발생: {str(e)}")
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": "❗ 서버 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
                    }
                }]
            }
        }), 200

# ✅ ChatGPT에게 질문하고 결과 저장
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
        answers[qid] = f"⚠️ ChatGPT 호출 중 오류 발생: {str(e)}"

# ✅ 사용자에게 GPT 답변을 보여주는 링크
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

# ✅ Render에서 외부 포트로 실행되도록 설정
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
