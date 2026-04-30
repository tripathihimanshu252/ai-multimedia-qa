import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import api from '../api/axios'

const s = {
  page:   { maxWidth:'900px', margin:'0 auto', padding:'32px 20px' },
  h1:     { fontSize:'26px', fontWeight:700, marginBottom:'6px' },
  sub:    { color:'#888', fontSize:'14px', marginBottom:'32px' },
  dz:     { border:'2px dashed #2a2d3e', borderRadius:'12px', padding:'40px', textAlign:'center', cursor:'pointer', transition:'border .2s', marginBottom:'32px' },
  dzActive:{ border:'2px dashed #4f8ef7', background:'#1a2a3a' },
  dzIcon: { fontSize:'40px', marginBottom:'12px' },
  dzText: { color:'#888', fontSize:'14px' },
  badge:  { display:'inline-block', padding:'3px 10px', borderRadius:'20px', fontSize:'11px', fontWeight:600 },
  card:   { background:'#1a1d27', border:'1px solid #2a2d3e', borderRadius:'12px', padding:'20px', marginBottom:'12px', display:'flex', alignItems:'center', gap:'16px' },
  icon:   { fontSize:'28px', minWidth:'40px', textAlign:'center' },
  info:   { flex:1 },
  fname:  { fontWeight:600, fontSize:'15px', marginBottom:'4px' },
  meta:   { fontSize:'12px', color:'#666' },
  actions:{ display:'flex', gap:'8px' },
  btn:    { background:'#4f8ef7', border:'none', borderRadius:'8px', padding:'8px 16px', color:'#fff', fontSize:'13px', fontWeight:500 },
  btnGhost:{ background:'transparent', border:'1px solid #3a3d4e', borderRadius:'8px', padding:'8px 16px', color:'#aaa', fontSize:'13px' },
  empty:  { textAlign:'center', padding:'60px 20px', color:'#555' },
  prog:   { height:'3px', background:'#4f8ef7', borderRadius:'2px', marginTop:'8px', transition:'width .3s' },
  summary:{ background:'#0f1117', borderRadius:'8px', padding:'12px', marginTop:'8px', fontSize:'13px', color:'#aaa', lineHeight:1.6 }
}

const STATUS_COLOR = { processing:'#f59e0b', generating_summary:'#8b5cf6', indexing:'#06b6d4', completed:'#10b981', error:'#ef4444' }
const FILE_ICON = { pdf:'📄', audio:'🎵', video:'🎬', unknown:'📁' }

export default function Dashboard() {
  const [files, setFiles]     = useState([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress]   = useState(0)
  const [expanded, setExpanded]   = useState(null)
  const navigate = useNavigate()

  const loadFiles = async () => {
    try { const r = await api.get('/files'); setFiles(r.data) } catch {}
  }

  useEffect(() => { loadFiles(); const t = setInterval(loadFiles, 4000); return () => clearInterval(t) }, [])

  const onDrop = useCallback(async (accepted) => {
    if (!accepted.length) return
    setUploading(true); setProgress(10)
    const fd = new FormData()
    fd.append('file', accepted[0])
    try {
      setProgress(40)
      await api.post('/upload', fd, { headers:{ 'Content-Type':'multipart/form-data' } })
      setProgress(100)
      setTimeout(() => { setProgress(0); setUploading(false); loadFiles() }, 800)
    } catch (e) {
      alert(e.response?.data?.detail || 'Upload failed')
      setUploading(false); setProgress(0)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept:{ 'application/pdf':['.pdf'], 'audio/*':['.mp3','.wav','.m4a'], 'video/*':['.mp4','.mkv'] }, maxFiles:1
  })

  const deleteFile = async (id) => {
    if (!confirm('Delete this file?')) return
    try { await api.delete(`/files/${id}`); loadFiles() } catch {}
  }

  return (
    <div style={s.page}>
      <h1 style={s.h1}>My Files 📂</h1>
      <p style={s.sub}>Upload PDFs, audio, or video to start chatting with AI</p>

      <div {...getRootProps()} style={{...s.dz, ...(isDragActive ? s.dzActive : {})}}>
        <input {...getInputProps()} />
        <div style={s.dzIcon}>{uploading ? '⏳' : '☁️'}</div>
        <div style={s.dzText}>{isDragActive ? 'Drop it here!' : 'Drag & drop a file, or click to browse'}</div>
        <div style={{fontSize:'12px', color:'#555', marginTop:'6px'}}>PDF, MP3, WAV, MP4, MKV • Max 50MB</div>
        {uploading && <div style={{...s.prog, width:`${progress}%`}} />}
      </div>

      {files.length === 0
        ? <div style={s.empty}><div style={{fontSize:'48px'}}>📭</div><p style={{marginTop:'12px'}}>No files yet — upload one above!</p></div>
        : files.map(f => (
          <div key={f.id} style={s.card}>
            <div style={s.icon}>{FILE_ICON[f.type] || '📁'}</div>
            <div style={s.info}>
              <div style={s.fname}>{f.filename}</div>
              <div style={s.meta}>
                {f.type?.toUpperCase()} •{' '}
                <span style={{...s.badge, background: STATUS_COLOR[f.status]+'22', color: STATUS_COLOR[f.status]}}>
                  {f.status?.replace('_',' ')}
                </span>
              </div>
              {f.status === 'completed' && expanded === f.id && f.summary && (
                <div style={s.summary}>{f.summary}</div>
              )}
            </div>
            <div style={s.actions}>
              {f.status === 'completed' && (
                <>
                  <button style={s.btn} onClick={() => navigate(`/chat/${f.id}`)}>💬 Chat</button>
                  <button style={s.btnGhost} onClick={() => setExpanded(expanded === f.id ? null : f.id)}>
                    {expanded === f.id ? 'Hide' : '📋 Summary'}
                  </button>
                </>
              )}
              <button style={{...s.btnGhost, color:'#ef4444'}} onClick={() => deleteFile(f.id)}>🗑</button>
            </div>
          </div>
        ))
      }
    </div>
  )
}
