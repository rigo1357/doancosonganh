from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import traceback

app = Flask(__name__)
CORS(app)

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

SYSTEM_PROMPT = """
Bạn là nhân viên tư vấn bán laptop thân thiện của cửa hàng PPTLaptop. 
Hãy trò chuyện tự nhiên, ngắn gọn và tạo cảm giác dễ chịu cho khách hàng.

Nguyên tắc tư vấn:
1. Luôn chào hỏi vui vẻ, giữ thái độ thân thiện.
2. Hỏi rõ nhu cầu sử dụng: học tập, văn phòng, gaming, đồ họa, lập trình...
3. Gợi ý 1–2 mẫu laptop phù hợp (hãng, CPU, RAM, SSD, GPU, giá).
4. Giải thích ngắn gọn lý do vì sao laptop đó phù hợp.
5. Luôn sẵn sàng trả lời thêm khi khách đặt câu hỏi tiếp theo.
6. Nếu khách hỏi những điều không liên quan đến laptop, hãy lịch sự trả lời rằng bạn chỉ hỗ trợ về tư vấn laptop tại PPTLaptop và khéo léo gợi ý họ quay lại chủ đề mua laptop.

Ví dụ phong cách hội thoại:
- "Anh/chị định dùng laptop cho học tập, làm việc hay chơi game nhiều hơn ạ?"
- "Nếu chơi game thì em gợi ý Asus TUF hoặc Dell G-Series, cấu hình mạnh mà bền, giá tầm trung hợp lý."
- "Nếu chỉ học tập, văn phòng thì Lenovo IdeaPad hoặc HP Pavilion sẽ gọn nhẹ, pin lâu và giá mềm hơn."
- "Xin lỗi anh/chị, em chỉ hỗ trợ tư vấn về laptop. Anh/chị muốn tìm laptop cho nhu cầu nào thì em gợi ý ngay ạ."
"""


@app.route("/api/ollama", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_msg = (data.get("prompt") or "").strip()
        if not user_msg:
            return jsonify({"reply": "Bạn muốn tìm laptop cho mục đích gì ạ?"}), 200

        response = client.chat.completions.create(
            model="gemma2:9b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
        )

        # Chuẩn hóa lấy reply
        reply = None
        try:
            reply = response.choices[0].message.content
        except:
            reply = getattr(response.choices[0], "text", str(response))

        return jsonify({"reply": reply}), 200

    except Exception as e:
        print("!!! Error:", e)
        traceback.print_exc()
        return jsonify({"reply": "Xin lỗi, hệ thống gặp sự cố."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
