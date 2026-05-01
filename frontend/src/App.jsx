import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Login from "./components/Login";
import Register from "./components/Register";
import Navbar from "./components/Navbar";
import FileUpload from "./components/FileUpload";
import FileList from "./components/FileList";
import ChatPanel from "./components/ChatPanel";
import MediaPlayer from "./components/MediaPlayer";

function PrivateRoute({ children }) {
  return localStorage.getItem("token") ? children : <Navigate to="/login" replace />;
}

function Dashboard() {
  const [refresh, setRefresh]         = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [jumpTo, setJumpTo]           = useState(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-6">
            <FileUpload onUploaded={() => setRefresh(r => r + 1)} />
            <FileList refreshTrigger={refresh} onSelectFile={setSelectedFile}
              selectedId={selectedFile?.id || selectedFile?._id} />
          </div>
          <div className="lg:col-span-2 space-y-6">
            {selectedFile ? (
              <>
                <MediaPlayer file={selectedFile} jumpTo={jumpTo} />
                <ChatPanel file={selectedFile} onTimestamp={setJumpTo} />
              </>
            ) : (
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm flex flex-col items-center justify-center h-96 text-gray-400">
                <div className="text-6xl mb-4">🎙️</div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">Select a file to begin</h3>
                <p className="text-sm text-center px-8">Upload a PDF, audio, or video file — then chat with AI about its contents</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
      <Routes>
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/"         element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="*"         element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
