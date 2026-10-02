import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import {PieChart,Pie,Tooltip,Cell,ResponsiveContainer} from "recharts";
import "./style.css";

const API="http://127.0.0.1:5000/api";
const empty={company:"",role:"",location:"",applied_date:new Date().toISOString().slice(0,10),interview_date:"",status:"Applied",notes:""};

function App(){
 const [token,setToken]=useState(localStorage.getItem("token"));
 const [user,setUser]=useState(JSON.parse(localStorage.getItem("user")||"null"));
 const [mode,setMode]=useState("login");
 const [jobs,setJobs]=useState([]); const [stats,setStats]=useState({total:0,counts:{}});
 const [form,setForm]=useState(empty); const [editing,setEditing]=useState(null);
 const [q,setQ]=useState(""); const [status,setStatus]=useState(""); const [message,setMessage]=useState("");

 const api=async(path,opt={})=>{const r=await fetch(API+path,{...opt,headers:{"Content-Type":"application/json","Authorization":"Bearer "+token,...(opt.headers||{})}}); const d=await r.json(); if(!r.ok) throw Error(d.message||"Request failed"); return d};
 const load=async()=>{try{setJobs(await api("/jobs?q="+encodeURIComponent(q)+"&status="+encodeURIComponent(status)));setStats(await api("/dashboard"))}catch(e){setMessage(e.message)}};
 useEffect(()=>{if(token) load()},[token,q,status]);

 async function auth(e){e.preventDefault();setMessage("");const data={email:e.target.email.value,password:e.target.password.value};if(mode==="register")data.name=e.target.name.value;try{const d=await fetch(API+"/auth/"+(mode==="login"?"login":"register"),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});const x=await d.json();if(!d.ok)throw Error(x.message);localStorage.setItem("token",x.token);localStorage.setItem("user",JSON.stringify(x.user));setToken(x.token);setUser(x.user)}catch(e){setMessage(e.message)}}
 const save=async(e)=>{e.preventDefault();try{if(editing)await api("/jobs/"+editing,{method:"PUT",body:JSON.stringify(form)});else await api("/jobs",{method:"POST",body:JSON.stringify(form)});setForm(empty);setEditing(null);load()}catch(e){setMessage(e.message)}};
 const edit=j=>{setEditing(j.id);setForm({...j})};
 const del=async id=>{if(confirm("Delete this application?")){await api("/jobs/"+id,{method:"DELETE"});load()}};
 const logout=()=>{localStorage.clear();setToken(null);setUser(null)};
 if(!token)return <div className="auth"><div className="auth-card"><h1>JobTrack</h1><p>Smart Job Application Tracker</p><form onSubmit={auth}>{mode==="register"&&<input name="name" placeholder="Full name" required/>}<input name="email" type="email" placeholder="Email" required/><input name="password" type="password" placeholder="Password (6+ chars)" required/><button>{mode==="login"?"Login":"Create account"}</button></form>{message&&<div className="msg">{message}</div>}<button className="link" onClick={()=>setMode(mode==="login"?"register":"login")}>{mode==="login"?"Create an account":"Back to login"}</button></div></div>;
 const chart=Object.entries(stats.counts||{}).map(([name,value])=>({name,value})).filter(x=>x.value);
 return <div><header><div><b>JobTrack</b><span> · Welcome, {user?.name}</span></div><button onClick={logout}>Logout</button></header><main>
 <section className="hero"><div><h1>Application Dashboard</h1><p>Track your job search from application to offer.</p></div></section>
 <section className="cards"><div><small>Total Applications</small><strong>{stats.total}</strong></div>{Object.entries(stats.counts||{}).map(([k,v])=><div key={k}><small>{k}</small><strong>{v}</strong></div>)}</section>
 <div className="grid"><section className="panel"><h2>{editing?"Edit Application":"Add Application"}</h2><form className="jobform" onSubmit={save}>{["company","role","location","applied_date","interview_date"].map(k=><input key={k} type={k.includes("date")?"date":"text"} placeholder={k.replace("_"," ")} value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})} required={["company","role","applied_date"].includes(k)}/>)}<select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{["Applied","Interview","Offer","Rejected"].map(x=><option key={x}>{x}</option>)}</select><textarea placeholder="Notes" value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})}/><button>{editing?"Update":"Add Application"}</button>{editing&&<button type="button" className="secondary" onClick={()=>{setEditing(null);setForm(empty)}}>Cancel</button>}</form></section>
 <section className="panel chart"><h2>Status Overview</h2>{chart.length?<ResponsiveContainer width="100%" height={240}><PieChart><Pie data={chart} dataKey="value" nameKey="name" outerRadius={85} label>{chart.map((_,i)=><Cell key={i}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer>:<p>No applications yet.</p>}</section></div>
 <section className="panel"><div className="toolbar"><h2>Applications</h2><input placeholder="Search company, role..." value={q} onChange={e=>setQ(e.target.value)}/><select value={status} onChange={e=>setStatus(e.target.value)}><option value="">All statuses</option>{["Applied","Interview","Offer","Rejected"].map(x=><option key={x}>{x}</option>)}</select></div><div className="tablewrap"><table><thead><tr><th>Company</th><th>Role</th><th>Location</th><th>Applied</th><th>Interview</th><th>Status</th><th>Actions</th></tr></thead><tbody>{jobs.map(j=><tr key={j.id}><td>{j.company}</td><td>{j.role}</td><td>{j.location||"—"}</td><td>{j.applied_date}</td><td>{j.interview_date||"—"}</td><td><span className={"badge "+j.status.toLowerCase()}>{j.status}</span></td><td><button className="tiny" onClick={()=>edit(j)}>Edit</button> <button className="tiny danger" onClick={()=>del(j.id)}>Delete</button></td></tr>)}{!jobs.length&&<tr><td colSpan="7" className="empty">No applications found.</td></tr>}</tbody></table></div></section>
 </main></div>
}
createRoot(document.getElementById("root")).render(<App/>);
