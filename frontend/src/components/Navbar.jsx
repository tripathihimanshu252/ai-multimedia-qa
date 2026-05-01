import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const auth = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    if (auth) auth.logout()
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    navigate('/login')
  }

  return (
    <nav style={{
      background:'#1a1d27', borderBottom:'1px solid #2a2d3e',
      padding:'0 24px', height:'60px', display:'flex',
      alignItems:'center', justifyContent:'space-between',
      position:'sticky', top:0, zIndex:100
    }}>
      <span style={{fontSize:'20px', fontWeight:700, color:'#4f8ef7', letterSpacing:'-0.5px'}}>
        🎯 AI Multimedia Q&A
      </span>
      <div style={{display:'flex', alignItems:'center', gap:'16px'}}>
        {auth?.user && (
          <span style={{fontSize:'14px', color:'#888'}}>👤 {auth.user.username}</span>
        )}
        <button
          onClick={handleLogout}
          style={{background:'#2a2d3e', border:'1px solid #3a3d4e', color:'#e0e0e0',
            padding:'7px 16px', borderRadius:'8px', fontSize:'13px', cursor:'pointer'}}>
          Logout
        </button>
      </div>
    </nav>
  )
}
