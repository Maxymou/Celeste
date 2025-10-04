import React from 'react'
import { Tabs } from './components/Tabs'
import { health } from './api'

export default function App() {
  const [tab, setTab] = React.useState<"Canton"|"Portée"|"Support"|"Câble"|"Température">("Portée")
  const [status, setStatus] = React.useState<string>('unknown')

  async function check() {
    try {
      const r = await health()
      setStatus(r.status)
    } catch(e:any) {
      setStatus('error')
    }
  }

  return (
    <div style={{fontFamily:'system-ui, Arial', maxWidth:980, margin:'0 auto', padding:16}}>
      <h1>CELESTE X</h1>
      <Tabs active={tab} onChange={setTab}/>
      <div style={{marginTop:16}}>
        <button onClick={check}>Health check</button>
        <span style={{marginLeft:12}}>status: <b>{status}</b></span>
      </div>
      <div style={{marginTop:24}}>
        <p>Tab actif : <b>{tab}</b> — formulaires et résultats viendront ici.</p>
      </div>
    </div>
  )
}
