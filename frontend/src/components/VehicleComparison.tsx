import React, { useState } from 'react'
import { Check, AlertTriangle, Scale } from 'lucide-react'
import type { VehicleProfile, FullVehicleCalculationResponse } from '../types'
import { SpecificationStatus } from './SpecificationStatus'

interface VehicleComparisonProps {
  profiles: Record<string, VehicleProfile>
  calculations: Record<string, FullVehicleCalculationResponse | null>
  currentProfileId: string
}

export const VehicleComparison: React.FC<VehicleComparisonProps> = ({
  profiles,
  calculations,
  currentProfileId,
}) => {
  // Support selecting 2 or 3 profiles for comparison
  const allProfileIds = Object.keys(profiles)
  const [selectedIds, setSelectedIds] = useState<string[]>(() => {
    // Default to Creta and Nexon 1.2
    const initial = [currentProfileId]
    const other = allProfileIds.find(id => id !== currentProfileId)
    if (other) initial.push(other)
    return initial
  })

  const toggleProfile = (id: string) => {
    if (selectedIds.includes(id)) {
      if (selectedIds.length > 2) {
        setSelectedIds(selectedIds.filter(x => x !== id))
      }
    } else {
      if (selectedIds.length < 3) {
        setSelectedIds([...selectedIds, id])
      } else {
        // Replace last item
        setSelectedIds([selectedIds[0], selectedIds[1], id])
      }
    }
  }

  const comparedProfiles = selectedIds.map(id => profiles[id]).filter(Boolean)

  const renderValWithUnit = (item: any, unitOverride?: string) => {
    if (!item || item.value === null || item.value === undefined) {
      return (
        <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>
          N/A — specification unavailable
        </span>
      )
    }

    const val = typeof item.value === 'number' ? Number(item.value).toFixed(2) : String(item.value)
    const unit = unitOverride || item.unit || ''

    return (
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, justifyContent: 'space-between' }}>
        <span>
          <strong>{val}</strong> {unit && <span style={{ fontSize: '0.8rem', color: '#64748b' }}>{unit}</span>}
        </span>
        <SpecificationStatus status={item.status} rationale={item.rationale} note={item.note} showText={false} />
      </div>
    )
  }

  const renderCalcVal = (calcObj: any, keyPath: string[], unit: string) => {
    if (!calcObj) {
      return <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>Calculating...</span>
    }

    let curr = calcObj
    for (const k of keyPath) {
      if (!curr) break
      curr = curr[k]
    }

    if (curr === null || curr === undefined || curr.status === 'unavailable') {
      return (
        <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>
          N/A — unavailable
        </span>
      )
    }

    const num = typeof curr.value === 'number' ? curr.value : (typeof curr === 'number' ? curr : null)
    if (num === null) {
      return <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>N/A</span>
    }

    return (
      <span>
        <strong>{num.toFixed(2)}</strong> <span style={{ fontSize: '0.8rem', color: '#64748b' }}>{unit}</span>
      </span>
    )
  }

  return (
    <div>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Scale size={20} />
            <span>Multi-Vehicle Engineering Specification Comparison</span>
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Side-by-side comparative inspection across Indian-market compact SUV powertrains. Select 2 or 3 vehicles.
          </p>
        </div>
      </div>

      {/* Vehicle Toggle Pills */}
      <div className="card" style={{ padding: '14px 20px', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
            Compare (select up to 3):
          </span>
          {Object.values(profiles).map(p => {
            const isSelected = selectedIds.includes(p.id)
            return (
              <button
                key={p.id}
                className={`btn ${isSelected ? 'btn-primary' : 'btn-outline'}`}
                style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                onClick={() => toggleProfile(p.id)}
              >
                {isSelected && <Check size={14} />}
                <span>{p.manufacturer} {p.name} ({p.variant})</span>
              </button>
            )
          })}
        </div>
      </div>

      <div className="alert-box alert-box-info" style={{ marginBottom: 20 }}>
        <AlertTriangle size={18} />
        <div>
          <strong>Comparison Methodology:</strong> Values are derived from official manufacturer specifications.
          Calculations are performed by the exact same verified Python physics engine. Where parameters like gear ratios
          or clutch dimensions are unreleased by manufacturers, values are marked <code>N/A — specification unavailable</code>
          rather than substituted with reference car values.
        </div>
      </div>

      {/* Main Comparison Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-wrapper" style={{ margin: 0, border: 'none' }}>
          <table className="calc-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th style={{ width: '28%' }}>Parameter / Specification</th>
                {comparedProfiles.map(p => (
                  <th key={p.id} style={{ width: `${72 / comparedProfiles.length}%`, textAlign: 'left' }}>
                    <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
                      {p.manufacturer} {p.name}
                    </div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)' }}>
                      {p.variant} ({p.model_year})
                    </div>
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {/* Section: Engine */}
              <tr style={{ background: '#f1f5f9' }}>
                <td colSpan={comparedProfiles.length + 1} style={{ fontWeight: 700, color: '#334155' }}>
                  1. ENGINE SPECIFICATIONS
                </td>
              </tr>
              <tr>
                <td>Displacement</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.engine.displacement_cc, 'cc')}</td>
                ))}
              </tr>
              <tr>
                <td>Cylinders</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.engine.cylinders, 'cyl')}</td>
                ))}
              </tr>
              <tr>
                <td>Maximum Power</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.engine.max_power_kw, 'kW')}</td>
                ))}
              </tr>
              <tr>
                <td>Rated Power Speed</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.engine.rated_power_rpm, 'rpm')}</td>
                ))}
              </tr>
              <tr>
                <td>Maximum Torque</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.engine.max_torque_nm, 'Nm')}</td>
                ))}
              </tr>
              <tr>
                <td>Torque Peak / Plateau Range</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.engine.torque_rpm_range, 'rpm')}</td>
                ))}
              </tr>

              {/* Section: Transmission */}
              <tr style={{ background: '#f1f5f9' }}>
                <td colSpan={comparedProfiles.length + 1} style={{ fontWeight: 700, color: '#334155' }}>
                  2. TRANSMISSION & DRIVETRAIN
                </td>
              </tr>
              <tr>
                <td>Transmission Type</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}><strong>{p.transmission}</strong> ({p.drivetrain})</td>
                ))}
              </tr>
              <tr>
                <td>Gear Ratios Published?</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {p.transmission_ratios.gear_ratios.value ? (
                      <span className="badge badge-success">Verified 6MT Ratios</span>
                    ) : (
                      <span className="badge badge-warning">N/A — Proprietary Service Data</span>
                    )}
                  </td>
                ))}
              </tr>
              <tr>
                <td>1st Gear Ratio</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {p.transmission_ratios.gear_ratios.value?.[1] ? (
                      <strong>{p.transmission_ratios.gear_ratios.value[1].toFixed(3)}</strong>
                    ) : (
                      <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>N/A</span>
                    )}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Final Drive Ratio</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.transmission_ratios.final_drive_ratio, '-')}</td>
                ))}
              </tr>

              {/* Section: Dimensions & Chassis */}
              <tr style={{ background: '#f1f5f9' }}>
                <td colSpan={comparedProfiles.length + 1} style={{ fontWeight: 700, color: '#334155' }}>
                  3. DIMENSIONS & WEIGHT
                </td>
              </tr>
              <tr>
                <td>Length × Width × Height</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {p.dimensions.length_mm.value} × {p.dimensions.width_mm.value} × {p.dimensions.height_mm.value} mm
                  </td>
                ))}
              </tr>
              <tr>
                <td>Wheelbase</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.dimensions.wheelbase_mm, 'mm')}</td>
                ))}
              </tr>
              <tr>
                <td>Ground Clearance</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.dimensions.ground_clearance_mm, 'mm')}</td>
                ))}
              </tr>
              <tr>
                <td>Kerb Mass</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.weights.kerb_mass_kg, 'kg')}</td>
                ))}
              </tr>
              <tr>
                <td>Gross Vehicle Weight (GVW)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.weights.gross_vehicle_mass_kg, 'kg')}</td>
                ))}
              </tr>
              <tr>
                <td>Tyre Specification</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>{renderValWithUnit(p.tyres.tyre_spec, '')}</td>
                ))}
              </tr>

              {/* Section: Calculated Engineering Results */}
              <tr style={{ background: '#e0f2fe' }}>
                <td colSpan={comparedProfiles.length + 1} style={{ fontWeight: 700, color: '#0369a1' }}>
                  4. CALCULATED ENGINEERING RESULTS (PYTHON ENGINE)
                </td>
              </tr>
              <tr>
                <td>Free Tyre Radius (r_free)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['basic_calculations', 'free_tyre_radius', 'value'], 'm')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Dynamic Rolling Radius (r)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['basic_calculations', 'dynamic_rolling_radius', 'value'], 'm')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Kerb Weight (W = M × g)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['basic_calculations', 'kerb_weight', 'value'], 'N')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Rated-Power Engine Torque (T_P)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['basic_calculations', 'torque_at_rated_power', 'value'], 'Nm')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Road Resistance @ 100 km/h (Kerb)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['road_resistance', 'kerb_mass', 'power_at_100kmh', 'total_resistance_N'], 'N')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Engine Power Req. @ 100 km/h (Kerb)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['road_resistance', 'kerb_mass', 'power_at_100kmh', 'engine_power_kw'], 'kW')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Max FWD Tractive Force (F_max Kerb)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['traction', 'kerb_mass', 'f_max_N'], 'N')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Maximum Gradeability Angle (θ)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['traction', 'kerb_mass', 'gradeability', 'gradeability_angle_deg'], 'deg')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>Maximum Gradient (G)</td>
                {comparedProfiles.map(p => (
                  <td key={p.id}>
                    {renderCalcVal(calculations[p.id], ['traction', 'kerb_mass', 'gradeability', 'gradient_percent'], '%')}
                  </td>
                ))}
              </tr>
              <tr>
                <td>1st Gear Tractive Effort (F_TW)</td>
                {comparedProfiles.map(p => {
                  const calc = calculations[p.id]
                  if (!calc || calc.drivetrain.status === 'incomplete' || !calc.drivetrain.gears['1']) {
                    return (
                      <td key={p.id}>
                        <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>
                          N/A — gear ratios unreleased
                        </span>
                      </td>
                    )
                  }
                  return (
                    <td key={p.id} className="val-bold">
                      {calc.drivetrain.gears['1'].tractive_effort_plateau_N.toFixed(1)} N
                    </td>
                  )
                })}
              </tr>
              <tr>
                <td>Clutch Design Torque (T_c)</td>
                {comparedProfiles.map(p => {
                  const calc = calculations[p.id]
                  if (!calc || !calc.clutch.results) {
                    return (
                      <td key={p.id}>
                        <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>
                          N/A — clutch dims unreleased
                        </span>
                      </td>
                    )
                  }
                  return (
                    <td key={p.id} className="val-bold">
                      {calc.clutch.results.design_torque_Tc_Nm.toFixed(1)} Nm
                    </td>
                  )
                })}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
