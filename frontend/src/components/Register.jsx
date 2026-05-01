import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import api from "../api/client"
import toast from "react-hot-toast"

export default function Register() {
  const [form, setForm] = useState({ username: "", email: "", password: "" })
  const [loading, setLoading] = useState(false)
  const nav = useNavigate()
  const auth = useAuth()

  const submit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await api.post("/api/auth/register", form)
      if (auth) auth.login(data.user || { username: form.username, email: form.email }, data.access_token)
      else localStorage.setItem("token", data.access_token)
      toast.success("Account created!")
      nav("/")
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed")
    } finally { setLoading(false) }
  }

  return (
    <div style={{minHeight:"100vh", display:"flex", alignItems:"center", justifyContent:"center", background:"#0f1117"}}>
      <div style={{background:"#1a1d27", borderRadius:"16px", border:"1px solid #2a2d3e", padding:"40px", width:"100%", maxWidth:"420px"}}>
        <div style={{textAlign:"center", marginBottom:"32px"}}>
          <div style={{fontSize:"40px", marginBottom:"12px"}}>🎯</div>
          <h1 style={{fontSize:"24px", fontWeight:"700", color:"#e0e0e0", margin:0}}>Create Account</h1>
          <p style={{color:"#666", fontSize:"14px", marginTop:"6px"}}>Join AI Multimedia Q&A</p>
        </div>
        <form onSubmit={submit}>
          {[
            {label:"Username", key:"username", type:"text", ph:"yourname"},
            {label:"Email", key:"email", type:"email", ph:"you@example.com"},
            {label:"Password", key:"password", type:"password", ph:"••••••••"}
          ].map(({label, key, type, ph}) => (
            <div key={key} style={{marginBottom:"16px"}}>
              <label style={{display:"block", fontSize:"13px", fontWeight:"600", color:"#aaa", marginBottom:"6px"}}>{label}</label>
              <input type={type} required value={form[key]}
                onChange={e => setForm({...form, [key]: e.target.value})}
                style={{width:"100%", background:"#0f1117", border:"1px solid #2a2d3e", borderRadius:"8px",
                  padding:"10px 14px", color:"#e0e0e0", fontSize:"14px", boxSizing:"border-box"}}
                placeholder={ph} />
            </div>
          ))}
          <button type="submit" disabled={loading}
            style={{width:"100%", background:"#4f8ef7", border:"none", borderRadius:"8px",
              padding:"12px", color:"white", fontWeight:"700", fontSize:"15px", cursor:"pointer",
              marginTop:"8px", opacity: loading ? 0.6 : 1}}>
            {loading ? "Creating..." : "Create Account"}
          </button>
        </form>
        <p style={{textAlign:"center", fontSize:"13px", color:"#666", marginTop:"24px"}}>
          Already have an account?{" "}
          <Link to="/login" style={{color:"#4f8ef7", textDecoration:"none", fontWeight:"600"}}>Sign in</Link>
        </p>
      </div>
    </div>
  )
}
