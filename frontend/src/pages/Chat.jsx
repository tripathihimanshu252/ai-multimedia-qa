import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import MediaPlayer from '../components/MediaPlayer'

const s = {
  page:   { display:'flex', height:'calc(100vh - 60px)', background:'#0f1117' },
  sidebar:{ width:'300px', borderRight:'1px solid #2a2d3e', padding:'20px', overflowY:'auto', background:'#1a1d27', flexShrink:0 },
  main:   { flex:1, display:'flex', flexDirection:'column' },
  chatWrap:{ flex:1, overflowY:'auto', padding:'20px' },
  inputRow:{ padding:'16px 20px', borderTop:'1px solid #2a2d3e', display:'flex', gap:'10px', background:'#1a1d27' },
  input:  { flex:1, background:'#0f1117', border:'1px solid #2a2d3e', borderRadius:'10px', padding:'12px 16px', color:'#e0e0e0', fontSize:'14px', outline:'none' },
  sendBtn:{ background:'#4f8ef7', border:'none', borderRadius:'10px', padding:'12px 20px', color:'#fff', fontWeight:600, fontSize:'14px' },
  bubble: { maxWidth:'80%', padding:'12px 16px', borderRadius:'12px', marginBottom:'14px', lineHeight:1.6, fontSize:'14px', whiteSpace:'pre-wrap' },
  user:   { background:'#4f8ef7', color:'#fff', marginLeft:'auto', borderBottomRightRadius:'4px' },
  bot:    { background:'#1a1d27', border:'1px solid #2a2d3e', color:'#e0e0e0', borderBottomLeftRadius:'4px' },
  ts:     { display:'flex', gap:'8px', marginTop:'8px', flexWrap:'wrap' },
  tsChip: { background:'#4f8ef722', border:'1px solid #4f8ef755', borderRadius:'20px', padding:'3px 10px', fontSize:'11px', color:'#4f8ef7', cursor:'pointer' },
  sideH:  { fontSize:'13px', color:'#888', marginBottom:'12px', textTransform:'uppercase', letterSpacing:'1px' },
  histItem:{ padding:'10px', borderRadius:'8px', marginBottom:'8px', background:'#0f1117', fontSize:'12px', color:'#aaa', cursor:'pointer' },
  back:   { background:'transparent', border:'1px solid #2a2d3e', borderRadius:'8px', padding:'8px 14px', color:'#aaa', fontSize:'13px', marginBottom:'16px' },
  cached: { fontSize:'11px', color:'#10b981', marginTop:'4px' }
}

export default function Chat() {
  const { fileId } = useParams()
  const navigate   = useNavigate()
  const [fileInfo, setFileInfo]   = useState(null)
  const [messages, setMessages]   = useState([])
  const [question, setQuestion]   = useState('')
  const [loading, setLoading]     = useState(false)
  const [history, setHistory]     = useState([])
  const [activeSegs, setActiveSegs] = useState([])
  const bottomRef = useRef(null)

  useEffect(() => {
    api.get(`/status/${fileId}`).then(r => setFileInfo(r.data)).catch(()=>{})
    api.get(`/chat/history/${fileId}`).then(r => {
      setHistory(r.data)
      const msgs = r.data.slice(0,10).reverse().flatMap(h => [
        { role:'user', text: h.question },
        { role:'bot',  text: h.answer, timestamps:[] }
      ])
      if (msgs.length) setMessages(msgs)
    }).catch(()=>{})
  }, [fileId])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior:'smooth' }) }, [messages])

  const sendMessage = async () => {
    if (!question.trim() || loading) return
    const q = question.trim()
    setQuestion('')
    setMessages(m => [...m, { role:'user', text:q }])
    setLoading(true)
    try {
      const res = await api.post('/chat', { file_id: fileId, question: q })
      const { answer, timestamps, cached } = res.data
      setMessages(m => [...m, { role:'bot', text:answer, timestamps, cached }])
      if (timestamps?.length) setActiveSegs(timestamps)
    } catch (e) {
      setMessages(m => [...m, { role:'bot', text:'⚠️ ' + (e.response?.data?.detail || 'Error getting answer') }])
    } finally { setLoading(false) }
  }

  const fmt = s => { const m=Math.floor(s/60); const sc=Math.floor(s%60); return `${String(m).padStart(2,'0')}:${String(sc).padStart(2,'0')}` }

  return (
    <div style={s.page}>
      {/* Sidebar */}
      <div style={s.sidebar}>
        <button style={s.back} onClick={() => navigate('/dashboard')}>← Back</button>
        {fileInfo && (
          <>
            <div style={{fontWeight:700, marginBottom:'4px', fontSize:'15px'}}>{fileInfo.filename}</div>
            <div style={{fontSize:'12px', color:'#888', marginBottom:'16px'}}>{fileInfo.type?.toUpperCase()} • {fileInfo.status}</div>
          </>
        )}
        {fileInfo && (fileInfo.type === 'audio' || fileInfo.type === 'video') && (
          <MediaPlayer fileId={fileId} fileType={fileInfo.type} segments={activeSegs} />
        )}
        {history.length > 0 && (
          <>
            <div style={{...s.sideH, marginTop:'20px'}}>📜 History</div>
            {history.slice(0,8).map((h,i) => (
              <div key={i} style={s.histItem} onClick={() => setQuestion(h.question)}>
                Q: {h.question.slice(0,60)}{h.question.length>60?'...':''}
              </div>
            ))}
          </>
        )}
      </div>

      {/* Chat area */}
      <div style={s.main}>
        <div style={s.chatWrap}>
          {messages.length === 0 && (
            <div style={{textAlign:'center', marginTop:'60px', color:'#555'}}>
              <div style={{fontSize:'48px', marginBottom:'16px'}}>💬</div>
              <p>Ask anything about your file!</p>
              <div style={{marginTop:'20px', display:'flex', gap:'10px', justifyContent:'center', flexWrap:'wrap'}}>
                {['Summarize this file', 'What are the main topics?', 'Give key insights'].map(q => (
                  <button key={q} style={s.tsChip} onClick={() => setQuestion(q)}>{q}</button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} style={{ display:'flex', flexDirection:'column', alignItems: m.role==='user'?'flex-end':'flex-start' }}>
              <div style={{...s.bubble, ...(m.role==='user' ? s.user : s.bot)}}>
                {m.text}
                {m.cached && <div style={s.cached}>⚡ Cached response</div>}
                {m.timestamps?.length > 0 && (
                  <div style={s.ts}>
                    {m.timestamps.map((t,ti) => (
                      <span key={ti} style={s.tsChip} onClick={() => setActiveSegs(m.timestamps)}>
                        ▶ {fmt(t.start)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{...s.bubble, ...s.bot, color:'#555'}}>🤔 Thinking...</div>
          )}
          <div ref={bottomRef} />
        </div>

        <div style={s.inputRow}>
          <input
            style={s.input}
            placeholder="Ask a question about your file..."
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
          />
          <button style={s.sendBtn} onClick={sendMessage} disabled={loading}>
            {loading ? '...' : 'Send ➤'}
          </button>
        </div>
      </div>
    </div>
  )
}
