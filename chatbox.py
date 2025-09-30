from flask import Flask, request, jsonify, session
from flask_cors import CORS
from openai import OpenAI
import traceback

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = "pptlaptop-secret"  # cần cho session

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

SYSTEM_PROMPT = """
Bạn là chuyên viên tư vấn laptop của cửa hàng PPTLaptop, luôn thân thiện, chuyên nghiệp và hiểu rõ các dòng máy trên thị trường.
Nhiệm vụ của bạn:
1. Luôn bắt đầu bằng việc hỏi rõ nhu cầu sử dụng của khách (học tập, văn phòng, gaming, đồ họa, lập trình, di chuyển nhiều, v.v.).
2. Sau khi biết nhu cầu, hãy gợi ý 1–2 mẫu laptop phù hợp nhất, nêu rõ hãng, cấu hình (CPU, RAM, SSD, GPU), giá bán, và lý do chọn mẫu đó.
3. Giải thích ngắn gọn, dễ hiểu, tập trung vào lợi ích thực tế cho khách hàng (ví dụ: "Mẫu này phù hợp vì pin lâu, màn hình đẹp, giá hợp lý cho sinh viên").
4. Nếu khách hỏi về khuyến mãi, trả góp, bảo hành, hãy trả lời chi tiết và chủ động đề xuất các ưu đãi của cửa hàng.
5. Luôn giữ thái độ lịch sự, không lặp lại chào hỏi, không trả lời lan man ngoài chủ đề laptop.
6. Nếu khách hỏi ngoài chủ đề laptop, hãy khéo léo chuyển hướng về tư vấn laptop.
7. Luôn sẵn sàng trả lời tiếp các câu hỏi bổ sung, không kết thúc hội thoại quá sớm.
8. Trả lời ngắn gọn, tự nhiên, giống như một nhân viên tư vấn thực thụ, không máy móc
"""

# Bộ nhớ hội thoại (demo dùng session Flask, có thể thay DB/Redis)
def get_history():
    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    return session["history"]

@app.route("/api/ollama", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_msg = (data.get("prompt") or "").strip()
        if not user_msg:
            return jsonify({"reply": "Bạn muốn tìm laptop cho mục đích gì ạ?"}), 200

        # Lấy lịch sử
        history = get_history()
        history.append({"role": "user", "content": user_msg})

        # Gọi API
        response = client.chat.completions.create(
            model="gemma2:9b",
            messages=history
        )

        reply = None
        try:
            if hasattr(response.choices[0], "message"):
                reply = response.choices[0].message.content
            elif hasattr(response.choices[0], "text"):
                reply = response.choices[0].text
        except Exception as e:
            print("Parse error:", e)

        if not reply:
            reply = "Xin lỗi, em chưa nghe rõ nhu cầu. Anh/chị muốn tìm laptop cho mục đích gì ạ?"

        # Lưu lại lịch sử
        history.append({"role": "assistant", "content": reply})
        session["history"] = history

        return jsonify({"reply": reply.strip()}), 200

    except Exception as e:
        print("!!! Error:", e)
        traceback.print_exc()
        return jsonify({"reply": "⚠️ Xin lỗi, hệ thống gặp sự cố."}), 500


@app.route("/api/ollama/reset", methods=["POST"])
def reset_chat():
    session.pop("history", None)
    return jsonify({"reply": "Đã khởi động lại hội thoại. Xin chào, bạn muốn tìm laptop cho nhu cầu nào ạ?"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
