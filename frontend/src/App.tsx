import { useState, useEffect } from 'react'
import { Activity, Bell, Users, FileText, LucideIcon } from 'lucide-react'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './components/Dashboard'
import { AlertsPanel } from './components/AlertsPanel'
import { PatrolsPanel } from './components/PatrolsPanel'
import { SummariesPanel } from './components/SummariesPanel'
import { API_BASE } from './config'
import { Alert, Patrol, Stats } from './types'
import './App.css'

export interface NavItem {
  id: string;
  icon: LucideIcon;
  label: string;
}

function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard')
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [patrols, setPatrols] = useState<Patrol[]>([])
  const [stats, setStats] = useState<Stats>({ alerts: 0, patrols: 0, active: 0, resolved: 0 })
  const [ws, setWs] = useState<WebSocket | null>(null)

  useEffect(() => {
    fetchAlerts()
    fetchPatrols()
    connectWebSocket()
    
    return () => ws?.close()
  }, [])

  const connectWebSocket = () => {
    try {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/realtime-alerts`
        console.log('Connecting to WS:', wsUrl)
        
        const socket = new WebSocket(wsUrl)
        socket.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.type === 'new_alert') {
            setAlerts(prev => [data.alert, ...prev])
            setStats(prev => ({ ...prev, alerts: prev.alerts + 1 }))
          }
        }
        setWs(socket)
    } catch(e) {
        console.error("WS Connect error", e)
    }
  }

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_BASE}/realtime-alerts?limit=20`)
      const data = await res.json()
      const items = Array.isArray(data) ? data : (data.items || [])
      setAlerts(items)
      setStats(prev => ({ ...prev, alerts: items.length }))
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

  const acknowledgeAlert = async (id: number) => {
    await fetch(`${API_BASE}/realtime-alerts/${id}/acknowledge`, { method: 'POST' })
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'acknowledged' } : a))
  }

  const navItems: NavItem[] = [
    { id: 'dashboard', icon: Activity, label: 'Dashboard' },
    { id: 'alerts', icon: Bell, label: 'Alert Center' },
    { id: 'patrols', icon: Users, label: 'Patrol Units' },
    { id: 'summaries', icon: FileText, label: 'Intel Briefs' },
  ]

  return (
    <div className="app">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} navItems={navItems} />

      <main className="main">
        <header className="header">
          <h2>{navItems.find(n => n.id === activeTab)?.label}</h2>
          <div className="header-actions">
            <button className="btn btn-ghost btn-sm">Help</button>
            <div className="live-indicator">
              <span className="live-dot"></span>
              System Active
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

export default App
