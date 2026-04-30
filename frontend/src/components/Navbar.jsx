import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

const s = {
  nav: { background:'#1a1d27', borderBottom:'1px solid #2a2d3e', padding:'0 24px', height:'60px', display:'flex', alignItems:'center', justifyContent:'space-between', position:'sticky', top:0, zIndex:100 },
  logo: { fontSize:'20px', fontWeight:700, color:'#4f8ef7', letterSpacing:'-0.5px' },
  right: { display:'flex', alignItems:'center', gap:'16px' },
  user: { fontSize:'14px', color:'#888' },
  btn: { background:'#2a2d3e', border:'1px solid #3a3d4e', color:'#e0e0e0', padding:'7px 16px', borderRadius:'8px', fontSize:'13px' }
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const handleLogout = () => { logout(); navigate('/login') }
  return (
    <nav style={s.nav}>
      <span style={s.logo}>🎯 AI Multimedia Q&A</span>
      <div style={s.right}>
        {user && <span style={s.user}>👤 {user.username}</span>}
        {user && <button style={s.btn} onClick={handleLogout}>Logout</button>}
      </div>
    </nav>
  )
}
