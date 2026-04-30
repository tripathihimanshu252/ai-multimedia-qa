import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'

const s = {
  wrap: { minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center', background:'#0f1117' },
  card: { background:'#1a1d27', border:'1px solid #2a2d3e', borderRadius:'16px', padding:'40px', width:'100%', maxWidth:'420px' },
  h1:   { fontSize:'24px', fontWeight:700, marginBottom:'6px', color:'#fff' },
  sub:  { color:'#888', fontSize:'14px', marginBottom:'28px' },
  label:{ display:'block', fontSize:'13px', color:'#aaa', marginBottom:'6px' },
  input:{ width:'100%', background:'#0f1117', border:'1px solid #2a2d3e', borderRadius:'8px', padding:'10px 14px', color:'#e0e0e0', fontSize:'14px', outline:'none', marginBottom:'16px' },
  btn:  { width:'100%', background:'#4f8ef7', border:'none', borderRadius:'8px', padding:'12px', color:'#fff', fontWeight:600, fontSize:'15px', marginTop:'8px' },
  err:  { background:'#2d1a1a', border:'1px solid #5a2a2a', borderRadius:'8px', padding:'10px 14px', color:'#ff6b6b', fontSize:'13px', marginBottom:'16px' },
  link: { textAlign:'center', marginTop:'20px', fontSize:'13px', color:'#888' }
}

export default function Register() {
  const [form, setForm]   = useState({ username:'', email:'', password:'' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate  = useNavigate()

  const handle = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const res = await api.post('/auth/register', form)
      login(res.data.user, res.data.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally { setLoading(false) }
  }

  return (
    <div style={s.wrap}>
      <div style={s.card}>
        <h1 style={s.h1}>Create account 🚀</h1>
        <p style={s.sub}>Get started for free</p>
        {error && <div style={s.err}>⚠️ {error}</div>}
        <form onSubmit={handle}>
          <label style={s.label}>Username</label>
          <input style={s.input} placeholder="cooluser" value={form.username}
            onChange={e => setForm({...form, username: e.target.value})} required />
          <label style={s.label}>Email</label>
          <input style={s.input} type="email" placeholder="you@email.com" value={form.email}
            onChange={e => setForm({...form, email: e.target.value})} required />
          <label style={s.label}>Password</label>
          <input style={s.input} type="password" placeholder="••••••••" value={form.password}
            onChange={e => setForm({...form, password: e.target.value})} required />
          <button style={s.btn} disabled={loading}>{loading ? 'Creating...' : 'Create Account'}</button>
        </form>
        <p style={s.link}>Already have an account? <Link to="/login" style={{color:'#4f8ef7'}}>Login</Link></p>
      </div>
    </div>
  )
}
