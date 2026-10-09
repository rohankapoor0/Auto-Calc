import React from 'react'
import {
  LayoutDashboard,
  Settings2,
  Gauge,
  Wind,
  ShieldAlert,
  CircleDot,
  GitFork,
  SlidersHorizontal,
  Scale,
} from 'lucide-react'

export type NavSection =
  | 'overview'
  | 'compare'
  | 'specifications'
  | 'basic'
  | 'drivetrain'
  | 'road_resistance'
  | 'traction'
  | 'clutch'
  | 'awd'

interface SidebarProps {
  activeSection: NavSection
  onSelectSection: (section: NavSection) => void
  vehicleName?: string
  isAwdSupported?: boolean
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSelectSection,
  vehicleName = 'Hyundai Creta',
  isAwdSupported = true,
}) => {
  const navItems: { id: NavSection; label: string; icon: React.ReactNode; isHypothetical?: boolean; disabled?: boolean }[] = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard size={18} /> },
    { id: 'compare', label: 'Compare Vehicles', icon: <Scale size={18} /> },
    { id: 'basic', label: 'Basic Calculations', icon: <Settings2 size={18} /> },
    { id: 'drivetrain', label: 'Drivetrain & Speeds', icon: <Gauge size={18} /> },
    { id: 'road_resistance', label: 'Road Resistance', icon: <Wind size={18} /> },
    { id: 'traction', label: 'Traction & Gradeability', icon: <ShieldAlert size={18} /> },
    { id: 'clutch', label: 'Clutch Design', icon: <CircleDot size={18} /> },
    {
      id: 'awd',
      label: 'AWD Analysis',
      icon: <GitFork size={18} />,
      isHypothetical: true,
      disabled: !isAwdSupported,
    },
    { id: 'specifications', label: 'Specifications', icon: <SlidersHorizontal size={18} /> },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand-title">
          <span>AutoCalc</span>
        </div>
        <div className="sidebar-brand-badge">Python Engine v1.0</div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map(item => (
          <button
            key={item.id}
            className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
            onClick={() => onSelectSection(item.id)}
            style={item.disabled ? { opacity: 0.45 } : {}}
            title={item.disabled ? 'AWD analysis is unavailable for standard FWD models' : undefined}
          >
            {item.icon}
            <span>{item.label}</span>
            {item.isHypothetical && (
              <span className="nav-item-badge-hypothetical">
                {item.disabled ? 'Disabled' : 'Hypothetical'}
              </span>
            )}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div><strong>Selected:</strong> {vehicleName}</div>
        <div><strong>Engine:</strong> Direct Python Process</div>
        <div style={{ marginTop: 4, fontSize: '0.7rem', color: '#94a3b8' }}>
          Zero runtime web APIs / DB
        </div>
      </div>
    </aside>
  )
}
