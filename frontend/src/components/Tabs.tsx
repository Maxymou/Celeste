import React from 'react'

const tabs = ["Canton", "Portée", "Support", "Câble", "Température"] as const
type Tab = typeof tabs[number]

export function Tabs({active, onChange}:{active:Tab, onChange:(t:Tab)=>void}) {
  return (
    <div style={{display:'flex', gap:8, padding:8, borderBottom:'1px solid #ddd'}}>
      {tabs.map(t => (
        <button key={t}
          onClick={()=>onChange(t)}
          style={{padding:'8px 12px', border:'1px solid #ccc', background: t===active ? '#eee' : '#fff', borderRadius:8}}>
          {t}
        </button>
      ))}
    </div>
  )
}
