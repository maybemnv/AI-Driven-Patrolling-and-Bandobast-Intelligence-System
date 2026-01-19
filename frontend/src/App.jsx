import { useState, useEffect } from 'react'
import { 
  Shield, Bell, Users, MapPin, FileText, Settings,
  AlertTriangle, CheckCircle, Clock, Activity
} from 'lucide-react'
import './App.css'

const API_BASE = '/api/v1'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [alerts, setAlerts] = useState([])
  const [patrols, setPatrols] = useState([])
  const [stats, setStats] = useState({ alerts: 0, patrols: 0, active: 0, resolved: 0 })
  const [ws, setWs] = useState(null)

  useEffect(() => {
    fetchAlerts()
    fetchPatrols()
    connectWebSocket()
    
    return () => ws?.close()
  }, [])

  const connectWebSocket = () => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/realtime-alerts`)
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'new_alert') {
        setAlerts(prev => [data.alert, ...prev])
        setStats(prev => ({ ...prev, alerts: prev.alerts + 1 }))
      }
    }
    setWs(socket)
  }

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_BASE}/realtime-alerts?limit=20`)
      const data = await res.json()
      setAlerts(data)
      setStats(prev => ({ ...prev, alerts: data.length }))
    } catch (e) {
      console.error('Fetch alerts error:', e)
    }
  }

  const fetchPatrols = async () => {
    try {
      const res = await fetch(`${API_BASE}/patrol/active`)
      const data = await res.json()
      setPatrols(data)
      setStats(prev => ({ ...prev, active: data.length }))
    } catch (e) {
      console.error('Fetch patrols error:', e)
    }
  }

  const acknowledgeAlert = async (id) => {
    await fetch(`${API_BASE}/realtime-alerts/${id}/acknowledge`, { method: 'POST' })
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'acknowledged' } : a))
  }

  const navItems = [
    { id: 'dashboard', icon: Activity, label: 'Dashboard' },
    { id: 'alerts', icon: Bell, label: 'Alerts' },
    { id: 'patrols', icon: Users, label: 'Patrols' },
    { id: 'summaries', icon: FileText, label: 'AI Summaries' },
  ]

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <Shield size={28} />
          <h1>Patrol Intel</h1>
        </div>
        <nav>
          <ul className="nav-menu">
            {navItems.map(item => (
              <li key={item.id} className="nav-item">
                <div 
                  className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(item.id)}
                >
                  <item.icon size={20} />
                  <span>{item.label}</span>
                </div>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      <main className="main">
        <header className="header">
          <h2>{navItems.find(n => n.id === activeTab)?.label}</h2>
          <div className="header-actions">
            <div className="live-indicator">
              <span className="live-dot"></span>
              Live
            </div>
          </div>
        </header>

        <div className="content">
          {activeTab === 'dashboard' && (
            <Dashboard stats={stats} alerts={alerts} patrols={patrols} />
          )}
          {activeTab === 'alerts' && (
            <AlertsPanel alerts={alerts} onAcknowledge={acknowledgeAlert} />
          )}
          {activeTab === 'patrols' && (
            <PatrolsPanel patrols={patrols} onRefresh={fetchPatrols} />
          )}
          {activeTab === 'summaries' && <SummariesPanel />}
        </div>
      </main>
    </div>
  )
}

function Dashboard({ stats, alerts, patrols }) {
  return (
    <>
      <div className="stats-grid">
        <StatCard icon={Bell} label="Active Alerts" value={stats.alerts} color="amber" />
        <StatCard icon={Users} label="Active Patrols" value={stats.active} color="blue" />
        <StatCard icon={CheckCircle} label="Resolved Today" value={stats.resolved} color="green" />
        <StatCard icon={AlertTriangle} label="Critical" value={alerts.filter(a => a.severity === 'critical').length} color="red" />
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Alerts</h3>
        </div>
        {alerts.slice(0, 5).map(alert => (
          <AlertItem key={alert.id} alert={alert} />
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Active Patrols</h3>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Officer</th>
              <th>Zone</th>
              <th>Started</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {patrols.map(p => (
              <tr key={p.id}>
                <td>{p.officer_name}</td>
                <td>{p.zone || '-'}</td>
                <td>{new Date(p.started_at).toLocaleTimeString()}</td>
                <td><span className="badge badge-success">Active</span></td>
              </tr>
            ))}
            {patrols.length === 0 && (
              <tr><td colSpan={4} style={{textAlign: 'center', color: 'var(--text-muted)'}}>No active patrols</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  )
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${color}`}>
        <Icon size={24} />
      </div>
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  )
}

function AlertItem({ alert, onAcknowledge }) {
  return (
    <div className={`alert-item ${alert.severity}`}>
      <AlertTriangle size={20} />
      <div className="alert-content">
        <div className="alert-type">{alert.alert_type}</div>
        <div className="alert-message">{alert.message}</div>
        <div className="alert-time">
          {alert.location && `📍 ${alert.location} • `}
          {new Date(alert.created_at).toLocaleString()}
        </div>
      </div>
      {alert.status === 'active' && onAcknowledge && (
        <button className="btn btn-sm btn-ghost" onClick={() => onAcknowledge(alert.id)}>
          Acknowledge
        </button>
      )}
    </div>
  )
}

function AlertsPanel({ alerts, onAcknowledge }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">All Alerts</h3>
        <span className="badge badge-info">{alerts.length} total</span>
      </div>
      {alerts.map(alert => (
        <AlertItem key={alert.id} alert={alert} onAcknowledge={onAcknowledge} />
      ))}
      {alerts.length === 0 && (
        <p style={{color: 'var(--text-muted)', textAlign: 'center', padding: '2rem'}}>No alerts</p>
      )}
    </div>
  )
}

function PatrolsPanel({ patrols, onRefresh }) {
  const [form, setForm] = useState({ officer_id: '', officer_name: '', zone: '' })

  const startPatrol = async () => {
    await fetch(`${API_BASE}/patrol/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    setForm({ officer_id: '', officer_name: '', zone: '' })
    onRefresh()
  }

  return (
    <>
      <div className="card">
        <h3 className="card-title" style={{marginBottom: '1rem'}}>Start New Patrol</h3>
        <div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap'}}>
          <input 
            placeholder="Officer ID" 
            value={form.officer_id}
            onChange={e => setForm({...form, officer_id: e.target.value})}
            style={{padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)'}}
          />
          <input 
            placeholder="Officer Name" 
            value={form.officer_name}
            onChange={e => setForm({...form, officer_name: e.target.value})}
            style={{padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)'}}
          />
          <input 
            placeholder="Zone" 
            value={form.zone}
            onChange={e => setForm({...form, zone: e.target.value})}
            style={{padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)'}}
          />
          <button className="btn btn-primary" onClick={startPatrol}>Start Patrol</button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Active Patrols</h3>
          <button className="btn btn-ghost btn-sm" onClick={onRefresh}>Refresh</button>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Officer</th>
              <th>Zone</th>
              <th>Started</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {patrols.map(p => (
              <tr key={p.id}>
                <td>#{p.id}</td>
                <td>{p.officer_name}</td>
                <td>{p.zone || '-'}</td>
                <td>{new Date(p.started_at).toLocaleString()}</td>
                <td><span className="badge badge-success">Active</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}

function SummariesPanel() {
  const [loading, setLoading] = useState(false)
  const [summaries, setSummaries] = useState([])
  const [selectedSummary, setSelectedSummary] = useState(null)

  useEffect(() => {
    fetchSummaries()
  }, [])

  const fetchSummaries = async () => {
    try {
      const res = await fetch(`${API_BASE}/summaries?limit=10`)
      const data = await res.json()
      // API returns { items: [], ... } or list. Handle both.
      setSummaries(data.items || data || [])
    } catch (e) {
      console.error('Fetch summaries error:', e)
    }
  }

  const generateBrief = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/summaries/generate/daily`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      })
      const data = await res.json()
      setSelectedSummary(data)
      fetchSummaries() // Refresh list
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">AI-Powered Summaries</h3>
          <button className="btn btn-primary" onClick={generateBrief} disabled={loading}>
            {loading ? 'Generating...' : 'Generate New Brief'}
          </button>
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem'}}>
        {/* List */}
        <div className="card">
          <h4 className="card-title" style={{marginBottom: '1rem'}}>History</h4>
          <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
            {summaries.map(s => (
              <div 
                key={s.id} 
                onClick={() => setSelectedSummary(s)}
                style={{
                  padding: '0.75rem', 
                  background: selectedSummary?.id === s.id ? 'var(--bg-secondary)' : 'var(--bg-primary)',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  border: '1px solid var(--border)'
                }}
              >
                <div style={{fontWeight: 500}}>{s.summary_type}</div>
                <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>
                  {new Date(s.created_at).toLocaleString()}
                </div>
              </div>
            ))}
            {summaries.length === 0 && <p style={{color: 'var(--text-muted)'}}>No summaries found.</p>}
          </div>
        </div>

        {/* Detail */}
        <div className="card">
          {selectedSummary ? (
            <>
              <div className="card-header">
                <div>
                  <h3 className="card-title">{selectedSummary.summary_type}</h3>
                  <div style={{fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem'}}>
                    {new Date(selectedSummary.created_at).toLocaleString()}
                  </div>
                </div>
                {selectedSummary.tokens_used && (
                  <span className="badge badge-info">
                    {selectedSummary.tokens_used} tokens
                  </span>
                )}
              </div>
              <div style={{marginTop: '1rem', whiteSpace: 'pre-wrap', color: 'var(--text-secondary)', lineHeight: 1.6}}>
                {selectedSummary.markdown || selectedSummary.raw_text}
              </div>
            </>
          ) : (
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px', color: 'var(--text-muted)'}}>
              Select a summary to view details
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
