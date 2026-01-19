import { Shield, LucideIcon } from 'lucide-react'

interface NavItem {
  id: string;
  icon: LucideIcon;
  label: string;
}

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  navItems: NavItem[];
}

export function Sidebar({ activeTab, setActiveTab, navItems }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-logo">
          <Shield size={32} />
        </div>
        <h1>Patrol Intel</h1>
      </div>
      <nav className="sidebar-nav">
        <ul className="nav-menu">
          {navItems.map(item => (
            <li key={item.id} className="nav-item">
              <button
                className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <item.icon size={22} />
                <span>{item.label}</span>
                {activeTab === item.id && <div className="nav-indicator" />}
              </button>
            </li>
          ))}
        </ul>
      </nav>
      <div className="sidebar-footer">
        <div className="user-access">
          <div className="user-avatar">AD</div>
          <div className="user-info">
            <span className="user-name">Admin User</span>
            <span className="user-role">Control Room</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
