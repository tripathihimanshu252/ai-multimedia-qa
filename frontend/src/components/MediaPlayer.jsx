import { useRef, useEffect } from 'react'

const s = {
  wrap: { background:'#1a1d27', border:'1px solid #2a2d3e', borderRadius:'12px', padding:'16px', marginTop:'16px' },
  title: { fontSize:'13px', color:'#888', marginBottom:'10px', textTransform:'uppercase', letterSpacing:'1px' },
  media: { width:'100%', borderRadius:'8px', outline:'none' },
  tsWrap: { marginTop:'12px', maxHeight:'180px', overflowY:'auto' },
  ts: { display:'flex', alignItems:'center', gap:'10px', padding:'8px 10px', borderRadius:'8px', marginBottom:'6px', background:'#0f1117', cursor:'pointer', fontSize:'13px', transition:'background .2s' },
  time: { background:'#4f8ef7', color:'#fff', padding:'2px 8px', borderRadius:'20px', fontSize:'11px', whiteSpace:'nowrap', minWidth:'80px', textAlign:'center' },
}

export default function MediaPlayer({ fileId, fileType, segments = [], token }) {
  const ref = useRef(null)
  const src = `/api/media/${fileId}`

  const jumpTo = (start) => {
    if (ref.current) { ref.current.currentTime = start; ref.current.play() }
  }

  const fmt = (sec) => {
    const m = Math.floor(sec / 60)
    const s = Math.floor(sec % 60)
    return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
  }

  if (!fileId || (fileType !== 'audio' && fileType !== 'video')) return null

  return (
    <div style={s.wrap}>
      <div style={s.title}>🎵 Media Player</div>
      {fileType === 'video'
        ? <video ref={ref} style={s.media} controls src={src} />
        : <audio ref={ref} style={s.media} controls src={src} />
      }
      {segments.length > 0 && (
        <div style={s.tsWrap}>
          <div style={{...s.title, marginTop:'12px'}}>⏱ Timestamps</div>
          {segments.map((seg, i) => (
            <div key={i} style={s.ts} onClick={() => jumpTo(seg.start)}
              onMouseEnter={e => e.currentTarget.style.background='#2a2d3e'}
              onMouseLeave={e => e.currentTarget.style.background='#0f1117'}>
              <span style={s.time}>{fmt(seg.start)} → {fmt(seg.end)}</span>
              <span style={{color:'#ccc', flex:1}}>{seg.text}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
