import { useEffect, useState } from "react";
import api from "../api/client";

const STATUS = {
  completed:          { emoji: "✅", label: "Ready",       color: "text-green-600 bg-green-50" },
  processing:         { emoji: "⏳", label: "Processing",  color: "text-yellow-600 bg-yellow-50" },
  generating_summary: { emoji: "🧠", label: "Summarizing", color: "text-blue-600 bg-blue-50" },
  error:              { emoji: "❌", label: "Error",        color: "text-red-600 bg-red-50" }
};

export default function FileList({ refreshTrigger, onSelectFile, selectedId }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try { const { data } = await api.get("/api/files"); setFiles(data); }
    catch {} finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [refreshTrigger]);

  useEffect(() => {
    const busy = files.some(f => f.status !== "completed" && f.status !== "error");
    if (!busy) return;
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, [files]);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Your Files</h2>
        <button onClick={load} className="text-xs text-teal-600 hover:underline">Refresh</button>
      </div>

      {loading ? (
        <div className="space-y-3 animate-pulse">
          {[1,2].map(i => <div key={i} className="h-14 bg-gray-100 rounded-lg" />)}
        </div>
      ) : files.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <div className="text-4xl mb-2">📂</div>
          <p className="text-sm">No files yet. Upload one above!</p>
        </div>
      ) : (
        <div className="space-y-2">
          {files.map(f => {
            const id = f.id || f._id;
            const cfg = STATUS[f.status] || STATUS.processing;
            const typeEmoji = f.type === "pdf" ? "📄" : f.type === "audio" ? "🎵" : "🎬";
            return (
              <button key={id} onClick={() => f.status === "completed" && onSelectFile(f)}
                className={`w-full flex items-center gap-3 p-3 rounded-xl text-left transition border
                  ${selectedId === id ? "border-teal-400 bg-teal-50" : "border-transparent hover:bg-gray-50"}
                  ${f.status !== "completed" ? "cursor-default opacity-70" : "cursor-pointer"}`}>
                <span className="text-xl">{typeEmoji}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-700 truncate">{f.filename}</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cfg.color}`}>
                    {cfg.emoji} {cfg.label}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
