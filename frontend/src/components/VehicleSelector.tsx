import React from 'react'
import { Car, ChevronDown } from 'lucide-react'
import type { VehicleProfile } from '../types'

interface VehicleSelectorProps {
  profiles: Record<string, VehicleProfile>
  selectedProfileId: string
  onSelectProfile: (profileId: string) => void
  disabled?: boolean
}

export const VehicleSelector: React.FC<VehicleSelectorProps> = ({
  profiles,
  selectedProfileId,
  onSelectProfile,
  disabled = false,
}) => {
  const currentProfile = profiles[selectedProfileId]

  return (
    <div className="vehicle-selector-bar">
      <div className="vehicle-selector-label">
        <Car size={18} color="#1e3a8a" />
        <span>Selected Vehicle Profile:</span>
      </div>

      <div className="vehicle-selector-dropdown-wrap">
        <select
          className="vehicle-selector-dropdown"
          value={selectedProfileId}
          onChange={e => onSelectProfile(e.target.value)}
          disabled={disabled}
        >
          {Object.values(profiles).map(p => (
            <option key={p.id} value={p.id}>
              {p.manufacturer} {p.name} — {p.variant} ({p.fuel_type}, {p.transmission})
            </option>
          ))}
        </select>
        <ChevronDown size={16} className="vehicle-selector-chevron" />
      </div>

      {currentProfile && (
        <div className="vehicle-selector-meta-pill">
          <span>MY: <strong>{currentProfile.model_year}</strong></span>
          <span>•</span>
          <span>Drivetrain: <strong>{currentProfile.drivetrain}</strong></span>
          <span>•</span>
          <span>Fuel: <strong>{currentProfile.fuel_type}</strong></span>
        </div>
      )}
    </div>
  )
}
