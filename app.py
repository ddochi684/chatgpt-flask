from flask import Flask, request, jsonify, redirect
import openai
import os
import threading
from uuid import uuid4

app = Flask(__name__) 

# 🔐 OpenAI API 키 환경변수에서 불러오기
openai.api_key = os.environ["OPENAI_API_KEY"]

# 💾 질문 ID별 답변 저장소 (메모리)
answers = {}

# ✅ 기본 확인용 루트
@app.route("/", methods=["GET"])
def index():
    return "GPT Chatbot is running!"

# ✅ 카카오 챗봇 Webhook 엔드포인트
@app.route("/chat", methods=["POST"])
def chat():
    try:
        # JSON 요청 파싱
        data = request.json
        print("✅ 카카오 요청 수신:", data)

        # 사용자 질문 추출
        user_input = data.get('userRequest', {}).get('utterance', '')
        if not user_input:
            raise ValueError("❗ 사용자 utterance 누락")

        # 고유 질문 ID 생성
        qid = str(uuid4())
        answers[qid] = "답변 준비 중입니다..."

        # 백그라운드 GPT 호출
        threading.Thread(target=ask_chatgpt_and_save, args=(qid, user_input)).start()

        # 안전한 안내 메시지 생성 (이모지 제거, 줄바꿈 정리)
        link = f"https://chatgpt-flask-af1v.onrender.com/answer?id={qid}"
        answer_msg = (
            "답변을 준비 중입니다.\n"
            "아래 링크에서 확인해 주세요:\n"
            f"{link}"
        )

        # 카카오 JSON 응답 (규격 준수)
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": answer_msg
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
                        "text": "❗ 서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
                    }
                }]
            }
        }), 200

# ✅ ChatGPT 호출 후 결과 저장
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
        answers[qid] = f"⚠️ ChatGPT 오류: {str(e)}"

# ✅ 사용자 링크로 GPT 답변 확인
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

# ✅ Render에서 사용할 포트 설정
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
