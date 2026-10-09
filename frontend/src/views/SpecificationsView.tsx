import React from 'react'
import { RotateCcw, AlertTriangle, Play, HelpCircle } from 'lucide-react'
import type { VehicleSpecifications, VehicleProfile } from '../types'
import { SpecificationStatus } from '../components/SpecificationStatus'

interface SpecificationsViewProps {
  specs: VehicleSpecifications | null
  metadata: Record<string, any>
  currentProfile?: VehicleProfile
  onChangeSpec: (key: string, value: any) => void
  onResetDefaults: () => void
  onCalculate: () => void
  isCalculating: boolean
  error?: string | null
}

export const SpecificationsView: React.FC<SpecificationsViewProps> = ({
  specs,
  metadata,
  currentProfile,
  onChangeSpec,
  onResetDefaults,
  onCalculate,
  isCalculating,
  error,
}) => {
  if (!specs) {
    return <div className="card">Loading specifications from Python backend...</div>
  }

  const getParamMeta = (paramKey: string) => {
    // Check metadata first
    if (metadata && metadata[paramKey]) {
      return metadata[paramKey]
    }
    // Check currentProfile structured data
    return null
  }

  const renderInputField = (
    key: string,
    label: string,
    unit: string,
    step: number = 0.01,
    min: number = 0,
    statusOverride?: string,
    rationale?: string
  ) => {
    const val = specs[key]
    const meta = getParamMeta(key)
    const status = statusOverride || meta?.status || 'assumed'
    const note = meta?.rationale || rationale

    return (
      <div className="form-group" key={key}>
        <div className="form-label-wrap">
          <label className="form-label">{label}</label>
          <SpecificationStatus status={status} rationale={note} />
        </div>
        <div className="form-input-wrap">
          <input
            type="number"
            className="form-input"
            step={step}
            min={min}
            placeholder="N/A (unavailable)"
            value={val !== null && val !== undefined ? val : ''}
            onChange={e => {
              const str = e.target.value
              onChangeSpec(key, str === '' ? null : (parseFloat(str) || 0))
            }}
          />
          {unit && <span className="form-unit">{unit}</span>}
        </div>
        {note && (
          <div style={{ fontSize: '0.72rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: 4 }}>
            <HelpCircle size={11} />
            <span>{note}</span>
          </div>
        )}
      </div>
    )
  }

  const gearRatios = specs.GEAR_RATIOS || {}

  return (
    <div>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
            Vehicle Engineering Specifications
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Active Profile: <strong>{currentProfile ? `${currentProfile.manufacturer} ${currentProfile.name} — ${currentProfile.variant}` : 'Hyundai Creta'}</strong>
          </p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn btn-outline" onClick={onResetDefaults} disabled={isCalculating} title="Reset profile to verified defaults">
            <RotateCcw size={15} />
            <span>Reset Profile Defaults</span>
          </button>
          <button className="btn btn-primary" onClick={onCalculate} disabled={isCalculating}>
            <Play size={15} fill="currentColor" />
            <span>Apply & Recalculate</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="alert-box alert-box-error">
          <AlertTriangle size={18} />
          <div>{error}</div>
        </div>
      )}

      {/* 1. Vehicle Mass & Dimensions */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">1. Vehicle Mass & Dimensions</h3>
        </div>
        <div className="form-grid">
          {renderInputField('KERB_MASS', 'Kerb Mass', 'kg', 1.0, 100, currentProfile?.weights.kerb_mass_kg.status)}
          {renderInputField('GROSS_VEHICLE_MASS', 'Gross Vehicle Mass (GVW)', 'kg', 1.0, 100, currentProfile?.weights.gross_vehicle_mass_kg.status)}
          {renderInputField('WHEELBASE', 'Wheelbase', 'm', 0.001, 0.5, currentProfile?.dimensions.wheelbase_mm.status)}
          {renderInputField('CG_HEIGHT', 'CG Height', 'm', 0.005, 0.1, currentProfile?.weights.cg_height_m.status, currentProfile?.weights.cg_height_m.rationale)}
          {renderInputField('FRONT_WEIGHT_SHARE', 'Front Weight Share (sf)', '-', 0.01, 0.01, currentProfile?.weights.front_weight_share.status, currentProfile?.weights.front_weight_share.rationale)}
          {renderInputField('GRAVITY', 'Gravity Constant (g)', 'm/s²', 0.01, 1.0, 'STANDARD CONSTANT')}
        </div>
      </div>

      {/* 2. Powertrain & Engine */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">2. Powertrain & Engine Output</h3>
        </div>
        <div className="form-grid">
          {renderInputField('MAX_POWER_KW', 'Max Engine Power', 'kW', 0.1, 10, currentProfile?.engine.max_power_kw.status)}
          {renderInputField('RATED_POWER_RPM', 'Rated Power Engine Speed', 'rpm', 50, 500, currentProfile?.engine.rated_power_rpm.status)}
          {renderInputField('MAX_ENGINE_TORQUE', 'Max Engine Torque', 'Nm', 1.0, 50, currentProfile?.engine.max_torque_nm.status)}
        </div>
      </div>

      {/* 3. Tyres & Wheels */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">3. Tyres & Wheels</h3>
        </div>
        <div className="form-grid">
          {renderInputField('TYRE_RIM_DIAMETER_IN', 'Rim Diameter', 'inch', 0.5, 10, currentProfile?.tyres.rim_diameter_in.status)}
          {renderInputField('TYRE_WIDTH_MM', 'Tyre Section Width', 'mm', 5.0, 100, currentProfile?.tyres.width_mm.status)}
          {renderInputField('TYRE_ASPECT_RATIO', 'Tyre Aspect Ratio', '%', 1.0, 20, currentProfile?.tyres.aspect_ratio.status)}
          {renderInputField('TYRE_DEFLECTION_FACTOR', 'Tyre Deflection Factor (fd)', '-', 0.005, 0.5, currentProfile?.tyres.deflection_factor.status, currentProfile?.tyres.deflection_factor.rationale)}
        </div>
      </div>

      {/* 4. Transmission & Drivetrain */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">4. Transmission & Drivetrain</h3>
        </div>
        <div className="card-description">
          {gearRatios && Object.keys(gearRatios).length > 0
            ? 'Forward transmission ratios (ig), final drive ratio (if), and efficiency.'
            : 'Note: Manufacturer has not published internal gear ratios for this vehicle. Enter custom ratios below to calculate speeds and tractive effort.'}
        </div>
        <div className="form-grid">
          {[1, 2, 3, 4, 5, 6].map(gear => {
            const hasRatio = gearRatios && gearRatios[gear] !== undefined && gearRatios[gear] !== null
            return (
              <div className="form-group" key={gear}>
                <div className="form-label-wrap">
                  <label className="form-label">Gear {gear} Ratio (i_{gear})</label>
                  <SpecificationStatus
                    status={hasRatio ? (currentProfile?.transmission_ratios.gear_ratios.status || 'verified') : 'unavailable'}
                  />
                </div>
                <div className="form-input-wrap">
                  <input
                    type="number"
                    className="form-input"
                    step={0.001}
                    placeholder="Unavailable"
                    value={hasRatio ? gearRatios[gear] : ''}
                    onChange={e => {
                      const str = e.target.value
                      const newRatios = { ...(gearRatios || {}) }
                      if (str === '') {
                        delete newRatios[gear]
                      } else {
                        newRatios[gear] = parseFloat(str) || 0
                      }
                      onChangeSpec('GEAR_RATIOS', Object.keys(newRatios).length > 0 ? newRatios : null)
                    }}
                  />
                  <span className="form-unit">-</span>
                </div>
              </div>
            )
          })}
          {renderInputField('FINAL_DRIVE_RATIO', 'Final Drive Ratio (if)', '-', 0.01, 0.5, currentProfile?.transmission_ratios.final_drive_ratio.status)}
          {renderInputField('TRANSMISSION_EFFICIENCY', 'Transmission Efficiency (ηT)', '-', 0.01, 0.1, currentProfile?.transmission_ratios.transmission_efficiency.status, currentProfile?.transmission_ratios.transmission_efficiency.rationale)}
        </div>
      </div>

      {/* 5. Aerodynamics & Road Resistance */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">5. Aerodynamics, Environment & Resistance</h3>
        </div>
        <div className="form-grid">
          {renderInputField('DRAG_COEFFICIENT', 'Drag Coefficient (CD)', '-', 0.01, 0.05, currentProfile?.aerodynamics_road.drag_coefficient.status, currentProfile?.aerodynamics_road.drag_coefficient.rationale)}
          {renderInputField('FRONTAL_AREA', 'Frontal Area (A)', 'm²', 0.05, 0.5, currentProfile?.aerodynamics_road.frontal_area_m2.status, currentProfile?.aerodynamics_road.frontal_area_m2.rationale)}
          {renderInputField('AIR_DENSITY', 'Air Density (ρ)', 'kg/m³', 0.005, 0.1, currentProfile?.aerodynamics_road.air_density_kg_m3.status, currentProfile?.aerodynamics_road.air_density_kg_m3.rationale)}
          {renderInputField('ROLLING_RESISTANCE_COEFFICIENT', 'Rolling Resistance Coeff. (fr)', '-', 0.001, 0.001, currentProfile?.aerodynamics_road.rolling_resistance_coeff.status, currentProfile?.aerodynamics_road.rolling_resistance_coeff.rationale)}
          {renderInputField('TYRE_ROAD_ADHESION', 'Road Adhesion Coeff. (μ)', '-', 0.01, 0.05, currentProfile?.aerodynamics_road.tyre_road_adhesion.status, currentProfile?.aerodynamics_road.tyre_road_adhesion.rationale)}
        </div>
      </div>

      {/* 6. Clutch System */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">6. Clutch Mechanism</h3>
        </div>
        <div className="form-grid">
          {renderInputField('CLUTCH_OUTER_DIAMETER_MM', 'Outer Diameter (OD)', 'mm', 1.0, 50, currentProfile?.clutch.outer_diameter_mm.status, currentProfile?.clutch.outer_diameter_mm.note)}
          {renderInputField('CLUTCH_INNER_DIAMETER_MM', 'Inner Diameter (ID)', 'mm', 1.0, 30, currentProfile?.clutch.inner_diameter_mm.status, currentProfile?.clutch.inner_diameter_mm.note)}
          {renderInputField('CLUTCH_FRICTION_COEFFICIENT', 'Friction Coeff. (μc)', '-', 0.01, 0.05, currentProfile?.clutch.friction_coefficient.status, currentProfile?.clutch.friction_coefficient.rationale)}
          {renderInputField('CLUTCH_FRICTION_SURFACES', 'Friction Surfaces (n)', '-', 1, 1, currentProfile?.clutch.friction_surfaces.status)}
          {renderInputField('CLUTCH_SAFETY_FACTOR', 'Safety Factor (SF)', '-', 0.05, 1.0, currentProfile?.clutch.safety_factor.status, currentProfile?.clutch.safety_factor.rationale)}
        </div>
      </div>
    </div>
  )
}
