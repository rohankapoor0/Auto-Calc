import React from 'react'
import { ExternalLink } from 'lucide-react'
import type { VehicleProfile } from '../types'

interface VehicleSummaryProps {
  profile: VehicleProfile
}

export const VehicleSummary: React.FC<VehicleSummaryProps> = ({ profile }) => {
  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
              {profile.manufacturer} {profile.name}
            </h2>
            <span className="badge badge-success" style={{ fontSize: '0.8rem' }}>
              {profile.variant}
            </span>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: 4, maxWidth: 650 }}>
            {profile.description}
          </p>
        </div>

        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: '#f8fafc', padding: '10px 14px', borderRadius: 6, border: '1px solid var(--border-color)' }}>
          <div><strong>Source:</strong> {profile.source_reference}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 4 }}>
            <span>Doc Type: <em>{profile.source_type}</em></span>
            {profile.source_url && (
              <a
                href={profile.source_url}
                target="_blank"
                rel="noreferrer"
                style={{ color: '#2563eb', display: 'inline-flex', alignItems: 'center', gap: 2, marginLeft: 8 }}
              >
                <span>View Source</span>
                <ExternalLink size={12} />
              </a>
            )}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 20, marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border-color)', fontSize: '0.825rem', flexWrap: 'wrap' }}>
        <div><strong>Wheelbase:</strong> {profile.dimensions.wheelbase_mm.value} mm</div>
        <div>•</div>
        <div><strong>Kerb Mass:</strong> {profile.weights.kerb_mass_kg.value} kg</div>
        <div>•</div>
        <div><strong>Power:</strong> {profile.engine.max_power_kw.value} kW @ {profile.engine.rated_power_rpm.value} rpm</div>
        <div>•</div>
        <div><strong>Torque:</strong> {profile.engine.max_torque_nm.value} Nm ({profile.engine.torque_rpm_range.value})</div>
        <div>•</div>
        <div><strong>Tyres:</strong> {profile.tyres.tyre_spec.value}</div>
      </div>
    </div>
  )
}
