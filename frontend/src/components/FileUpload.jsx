import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import api from "../api/client";
import toast from "react-hot-toast";

export default function FileUpload({ onUploaded }) {
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);

  const onDrop = useCallback(accepted => { if (accepted[0]) setFile(accepted[0]); }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [], "audio/*": [], "video/*": [] },
    maxFiles: 1, maxSize: 100 * 1024 * 1024
  });

  const upload = async () => {
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const { data } = await api.post("/api/upload", fd);
      toast.success("Uploaded! AI processing started...");
      onUploaded(data.id);
      setFile(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally { setUploading(false); }
  };

  const typeIcon = f => {
    if (!f) return "📁";
    if (f.type === "application/pdf") return "📄";
    if (f.type.startsWith("audio")) return "🎵";
    return "🎬";
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Upload File</h2>
      <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition
        ${isDragActive ? "border-teal-500 bg-teal-50" : "border-gray-200 hover:border-teal-400 hover:bg-gray-50"}`}>
        <input {...getInputProps()} />
        <div className="text-4xl mb-3">☁️</div>
        <p className="text-gray-600 font-medium">
          {isDragActive ? "Drop your file here!" : "Drag & drop or click to upload"}
        </p>
        <p className="text-xs text-gray-400 mt-1">PDF, MP3, WAV, MP4, MKV — max 100MB</p>
      </div>

      {file && (
        <div className="mt-4 flex items-center gap-3 bg-gray-50 rounded-lg p-3">
          <span className="text-xl">{typeIcon(file)}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-700 truncate">{file.name}</p>
            <p className="text-xs text-gray-400">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
          </div>
          <button onClick={() => setFile(null)} className="text-gray-400 hover:text-red-500 text-lg transition">✕</button>
        </div>
      )}

      <button onClick={upload} disabled={!file || uploading}
        className="mt-4 w-full bg-teal-600 hover:bg-teal-700 text-white font-semibold py-2.5 rounded-lg transition disabled:opacity-50">
        {uploading ? "Uploading..." : "Upload & Process"}
      </button>
    </div>
  );
}
