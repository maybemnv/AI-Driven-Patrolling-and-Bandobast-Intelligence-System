import { Bell, Users, CheckCircle, AlertTriangle, MapPin, Activity } from 'lucide-react'
import { StatCard } from './StatCard'
import { Alert, Patrol, Stats } from '../types'

interface DashboardProps {
  stats: Stats;
  alerts: Alert[];
  patrols: Patrol[];
}

export function Dashboard({ stats, alerts, patrols }: DashboardProps) {
  return (
    <div className="dashboard-container">
      {/* Stats Grid */}
      <div className="stats-grid">
        <StatCard icon={Bell} label="Active Alerts" value={stats.alerts} color="amber" />
        <StatCard icon={Users} label="Active Patrols" value={stats.active} color="blue" />
        <StatCard icon={CheckCircle} label="Resolved Today" value={stats.resolved} color="green" />
        <StatCard icon={AlertTriangle} label="Critical Level" value={alerts.filter(a => a.severity === 'critical').length} color="red" />
      </div>

      <div className="dashboard-content-grid">
        {/* Recent Alerts Column */}
        <section className="dashboard-section">
          <div className="section-header">
            <h3><Activity size={20} /> Live Feed</h3>
            <span className="badge badge-pulse">Live</span>
          </div>
          <div className="feed-list">
            {alerts.slice(0, 6).map(alert => (
              <div key={alert.id} className={`feed-item ${alert.severity}`}>
                <div className="feed-icon">
                  <AlertTriangle size={16} />
                </div>
                <div className="feed-details">
                  <span className="feed-type">{alert.alert_type}</span>
                  <p className="feed-message">{alert.message}</p>
                  <span className="feed-time">
                    {alert.location && <span><MapPin size={12}/> {alert.location} • </span>}
                    {new Date(alert.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
            {alerts.length === 0 && <div className="empty-state">No active alerts</div>}
          </div>
        </section>

        {/* Active Patrols Column */}
        <section className="dashboard-section">
          <div className="section-header">
            <h3><Users size={20} /> On Patrol</h3>
            <span className="badge">{patrols.length} Active</span>
          </div>
          <div className="patrol-list-compact">
            {patrols.map(p => (
              <div key={p.id} className="patrol-card-compact">
                <div className="patrol-avatar">{p.officer_name.charAt(0)}</div>
                <div className="patrol-info">
                  <div className="patrol-name">{p.officer_name}</div>
                  <div className="patrol-zone">Zone: {p.zone || 'N/A'}</div>
                </div>
                <div className="patrol-status">
                  <span className="status-dot"></span>
                </div>
              </div>
            ))}
            {patrols.length === 0 && <div className="empty-state">No patrols active</div>}
          </div>
        </section>
      </div>
    </div>
  )
}
