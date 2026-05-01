import { useState, useRef, useEffect } from "react";
import api from "../api/client";
import toast from "react-hot-toast";

export default function ChatPanel({ file, onTimestamp }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    setMessages([{ role: "assistant", content: `Hi! I've analyzed **${file.filename}**. Ask me anything!` }]);
  }, [file]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const send = async e => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const q = input.trim(); setInput("");
    setMessages(m => [...m, { role: "user", content: q }]);
    setLoading(true);
    try {
      const { data } = await api.post("/api/chat", { file_id: file.id || file._id, question: q });
      setMessages(m => [...m, { role: "assistant", content: data.answer, timestamps: data.timestamps || [], cached: data.cached }]);
    } catch (err) {
      const msg = err.response?.status === 429 ? "⏱️ Rate limit hit. Wait a moment." : err.response?.data?.detail || "Error";
      toast.error(msg);
      setMessages(m => [...m, { role: "assistant", content: msg, error: true }]);
    } finally { setLoading(false); }
  };

  const fmt = s => { const m = Math.floor(s/60); return `${m}:${Math.floor(s%60).toString().padStart(2,"0")}`; };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col" style={{height: "580px"}}>
      <div className="p-4 border-b border-gray-100">
        <h2 className="text-lg font-semibold text-gray-800">💬 Chat with AI</h2>
        <p className="text-xs text-gray-400 truncate">{file.filename}</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm flex-shrink-0
              ${msg.role === "user" ? "bg-teal-600 text-white" : "bg-gray-100"}`}>
              {msg.role === "user" ? "👤" : "🤖"}
            </div>
            <div className={`flex flex-col gap-1 max-w-[75%] ${msg.role === "user" ? "items-end" : ""}`}>
              <div className={`rounded-2xl px-4 py-2.5 text-sm
                ${msg.role === "user"
                  ? "bg-teal-600 text-white rounded-tr-sm"
                  : msg.error ? "bg-red-50 text-red-700" : "bg-gray-100 text-gray-800 rounded-tl-sm"}`}>
                {msg.content}
                {msg.cached && <span className="ml-2 text-xs opacity-60">⚡cached</span>}
              </div>
              {msg.timestamps?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {msg.timestamps.map((ts, j) => (
                    <button key={j} onClick={() => onTimestamp(ts.start)}
                      className="text-xs bg-teal-100 text-teal-700 hover:bg-teal-200 px-2 py-1 rounded-full transition">
                      ▶ {fmt(ts.start)} — {ts.text?.slice(0,28)}...
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-2">
            <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center text-sm">🤖</div>
            <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1">
              {[0,1,2].map(i => <div key={i} className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                style={{animationDelay:`${i*0.15}s`}} />)}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={send} className="p-4 border-t border-gray-100 flex gap-2">
        <input value={input} onChange={e => setInput(e.target.value)}
          placeholder="Ask anything about this file..."
          className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-300 focus:border-teal-500 transition" />
        <button type="submit" disabled={!input.trim() || loading}
          className="bg-teal-600 hover:bg-teal-700 text-white rounded-xl px-4 py-2.5 transition disabled:opacity-50 text-sm font-medium">
          Send
        </button>
      </form>
    </div>
  );
}
