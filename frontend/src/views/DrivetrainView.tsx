import React from 'react'
import { Play, AlertCircle } from 'lucide-react'
import type { DrivetrainOutput } from '../types'
import { FormulaAccordion } from '../components/FormulaAccordion'

interface DrivetrainViewProps {
  data: DrivetrainOutput | null
  onCalculate: () => void
  isCalculating: boolean
}

export const DrivetrainView: React.FC<DrivetrainViewProps> = ({
  data,
  onCalculate,
  isCalculating,
}) => {
  if (!data) {
    return (
      <div className="card">
        <p>No drivetrain calculations available yet.</p>
        <button className="btn btn-primary" onClick={onCalculate} style={{ marginTop: 12 }}>
          Run Drivetrain Analysis
        </button>
      </div>
    )
  }

  const formulasRecord: Record<string, string> = {
    'Tractive Effort (Formula 7)': data.formula_tractive_effort,
    'Vehicle Speed m/s (Formula 8)': data.formula_vehicle_speed_mps,
    'Vehicle Speed km/h (Formula 9)': data.formula_vehicle_speed_kmh,
    'Wheel Torque Demand (Formula 10)': data.formula_wheel_torque_demand,
    'Rated RPM Force Note':
      'At rated engine power RPM, tractive effort utilizes T_P rather than mid-range plateau torque.',
  }

  const gears = Object.values(data.gears || {}).sort((a, b) => a.gear - b.gear)

  return (
    <div>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
            Module B: Drivetrain, Tractive Effort & Speeds (Formulas 7 – 10)
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Evaluates gear-by-gear tractive force, torque demand, and road speeds at 1500, 2750, and 4000 rpm.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onCalculate} disabled={isCalculating}>
          <Play size={15} fill="currentColor" />
          <span>Recalculate Module</span>
        </button>
      </div>

      {data.status === 'incomplete' ? (
        <div className="card">
          <div className="alert-box alert-box-warning">
            <AlertCircle size={20} />
            <div>
              <strong>Calculations Incomplete:</strong> {data.note || 'Gear ratios and final drive ratio are unavailable from official manufacturer publications for this vehicle.'}
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            To protect engineering data integrity, the system does not substitute gear ratios from other vehicles.
            You can enter verified gear ratios in the <strong>Specifications</strong> tab to enable this calculation module.
          </p>
        </div>
      ) : (
        <div className="card">
          {/* Summary Highlight */}
          <div style={{ display: 'flex', gap: 24, alignItems: 'center', marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Rated Power Torque
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
                {data.rated_power_torque_Nm ? data.rated_power_torque_Nm.toFixed(2) : 'N/A'}{' '}
                <span style={{ fontSize: '0.9rem' }}>Nm</span>
              </div>
            </div>
          </div>

          {/* Complete Gear Matrix Table */}
          <div className="table-wrapper">
            <table className="calc-table">
              <thead>
                <tr>
                  <th>Gear</th>
                  <th>Gear Ratio (i_g)</th>
                  <th>Overall (i_o)</th>
                  <th>FTW @ Torque Peak (N)</th>
                  <th>Demand @ Peak (Nm)</th>
                  <th>FTW @ Rated RPM (N)</th>
                  <th>Speed @ 1500 rpm</th>
                  <th>Speed @ 2750 rpm</th>
                  <th>Speed @ 4000 rpm</th>
                </tr>
              </thead>
              <tbody>
                {gears.map(g => (
                  <tr key={g.gear}>
                    <td><strong>Gear {g.gear}</strong></td>
                    <td>{g.gear_ratio.toFixed(3)}</td>
                    <td>{g.overall_ratio.toFixed(3)}</td>
                    <td className="val-bold">{g.tractive_effort_plateau_N.toFixed(1)} N</td>
                    <td>{g.wheel_torque_demand_plateau_Nm.toFixed(1)} Nm</td>
                    <td style={{ color: '#0369a1', fontWeight: 600 }}>
                      {g.tractive_effort_4000rpm_N.toFixed(1)} N
                    </td>
                    <td>{g.speeds_by_rpm[1500]?.speed_kmh.toFixed(2)} km/h</td>
                    <td>{g.speeds_by_rpm[2750]?.speed_kmh.toFixed(2)} km/h</td>
                    <td className="val-bold">{g.speeds_by_rpm[4000]?.speed_kmh.toFixed(2)} km/h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <FormulaAccordion formulas={formulasRecord} />
        </div>
      )}
    </div>
  )
}
