const chatInput = document.getElementById('chat-input');

// Auto-grow textarea giống ChatGPT
chatInput.addEventListener('input', () => {
  chatInput.style.height = 'auto';  // reset trước
  chatInput.style.height = chatInput.scrollHeight + 'px';
});

function cleanText(text){
  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")   // bỏ **bold**
    .replace(/^\s*\*+\s*/gm, "- ")     // đổi * thành gạch đầu dòng
    .replace(/\([^)]*\)/g, "")         // bỏ (ghi chú)
    .replace(/\s{2,}/g, " ")           // xoá khoảng trắng thừa
    .trim();
}

async function sendChatMessage(){
  const t = chatInput.value.trim();
  if(!t) return;
  appendMsg(t,'user');
  chatInput.value = '';
  try{
    const res = await fetch('http://127.0.0.1:5000/api/ollama', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ prompt: t })
    });
    const data = await res.json();
    appendMsg(cleanText(data.reply || 'Xin lỗi, chưa có phản hồi.'),'bot');
  }catch(err){
    console.error('Chatbox error:', err);
    appendMsg('⚠️ Không thể kết nối máy chủ.','bot');
  }
}
