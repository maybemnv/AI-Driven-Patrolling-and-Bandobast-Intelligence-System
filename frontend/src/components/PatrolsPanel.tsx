import { useState, FormEvent } from 'react'
import { Plus, User, Map, RefreshCw } from 'lucide-react'
import { API_BASE } from '../config'
import { Patrol } from '../types'

interface PatrolsPanelProps {
  patrols: Patrol[];
  onRefresh: () => void;
}

interface PatrolForm {
  officer_id: string;
  officer_name: string;
  zone: string;
}

export function PatrolsPanel({ patrols, onRefresh }: PatrolsPanelProps) {
  const [form, setForm] = useState<PatrolForm>({ officer_id: '', officer_name: '', zone: '' })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const startPatrol = async (e: FormEvent) => {
    e.preventDefault()
    if(!form.officer_id || !form.officer_name) return
    
    setIsSubmitting(true)
    try {
      await fetch(`${API_BASE}/patrol/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      setForm({ officer_id: '', officer_name: '', zone: '' })
      onRefresh()
    } catch (e) {
      console.error(e)
    }
    setIsSubmitting(false)
  }

  return (
    <div className="panel-container">
      <div className="panel-split">
        {/* Start Patrol Form */}
        <div className="panel-section form-section">
          <h3>Start New Patrol</h3>
          <form onSubmit={startPatrol} className="patrol-form">
            <div className="form-group">
              <label>Officer ID</label>
              <div className="input-wrapper">
                <User size={18} />
                <input 
                  value={form.officer_id}
                  onChange={e => setForm({...form, officer_id: e.target.value})}
                  placeholder="e.g. OFF-001"
                />
              </div>
            </div>
            <div className="form-group">
              <label>Officer Name</label>
              <div className="input-wrapper">
                <User size={18} />
                <input 
                  value={form.officer_name}
                  onChange={e => setForm({...form, officer_name: e.target.value})}
                  placeholder="Name"
                />
              </div>
            </div>
            <div className="form-group">
              <label>Zone / Route</label>
              <div className="input-wrapper">
                <Map size={18} />
                <input 
                  value={form.zone}
                  onChange={e => setForm({...form, zone: e.target.value})}
                  placeholder="Zone A"
                />
              </div>
            </div>
            <button type="submit" className="btn btn-primary btn-block" disabled={isSubmitting}>
              {isSubmitting ? 'Starting...' : <><Plus size={18} /> Start Session</>}
            </button>
          </form>
        </div>

        {/* Active Patrols Table */}
        <div className="panel-section list-section">
          <div className="section-header">
            <h3>Active Sessions</h3>
            <button className="btn btn-ghost btn-sm btn-icon" onClick={onRefresh}>
              <RefreshCw size={16} />
            </button>
          </div>
          
          <div className="table-responsive">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Officer</th>
                  <th>Zone</th>
                  <th>Duration</th>
                </tr>
              </thead>
              <tbody>
                {patrols.map(p => (
                  <tr key={p.id}>
                    <td><span className="status-badge active">Active</span></td>
                    <td className="fw-500">{p.officer_name} <span className="text-muted text-xs">#{p.id}</span></td>
                    <td>{p.zone || '—'}</td>
                    <td className="font-mono text-sm">
                      {new Date(p.started_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
                {patrols.length === 0 && (
                  <tr>
                    <td colSpan={4} className="text-center text-muted py-4">No active patrols</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
