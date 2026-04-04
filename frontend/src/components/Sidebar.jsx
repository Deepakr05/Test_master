import { useLocation, useNavigate } from 'react-router-dom'

const NAV = [
  { path: '/dashboard', label: 'Dashboard', icon: '▤' },
  { path: '/generate',  label: 'Generate',  icon: '⚡' },
  { path: '/test-cases',label: 'Test Cases',icon: '📋' },
  { path: '/history',   label: 'History',   icon: '🕐' },
  { path: '/settings',  label: 'Settings',  icon: '⚙' },
]

export default function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <div className="sidebar fade-in">
      <div className="sidebar-brand">
        <div className="brand-icon">✨</div>
        <span className="brand-name">TestMaster</span>
      </div>

      <div className="sidebar-nav">
        {NAV.map(item => (
          <button
            key={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-version">TestMaster v1.0</div>
      </div>
    </div>
  )
}
