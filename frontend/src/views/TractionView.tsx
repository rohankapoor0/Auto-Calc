import React from 'react'
import { Play } from 'lucide-react'
import type { TractionOutput } from '../types'
import { FormulaAccordion } from '../components/FormulaAccordion'

interface TractionViewProps {
  data: TractionOutput | null
  onCalculate: () => void
  isCalculating: boolean
}

export const TractionView: React.FC<TractionViewProps> = ({
  data,
  onCalculate,
  isCalculating,
}) => {
  if (!data) {
    return (
      <div className="card">
        <p>No traction calculations available yet.</p>
        <button className="btn btn-primary" onClick={onCalculate} style={{ marginTop: 12 }}>
          Run Traction Analysis
        </button>
      </div>
    )
  }

  const kerb = data.kerb_mass
  const gvw = data.gross_vehicle_mass

  const formulasRecord: Record<string, string> = {
    'Static Front Axle Load (Formula 22)': data.formulas.static_front_load,
    'Static Rear Axle Load (Formula 23)': data.formulas.static_rear_load,
    'Max FWD Tractive Force (Formula 24)': data.formulas.max_tractive_force_fwd,
    'Wheel Spin Condition (Formula 25)': data.formulas.wheel_spin,
    'Traction Factor k (Formula 26)': data.formulas.traction_factor,
    'Gradeability Angle (Formula 27)': data.formulas.gradeability_angle,
    'Gradient Percentage (Formula 28)': data.formulas.gradient_percentage,
    'Longitudinal Load Transfer (Formula 29)': data.formulas.longitudinal_transfer,
    'Dynamic Front Load (Formula 30)': data.formulas.dynamic_front_load,
    'Tyre Slip Torque (Formula 31)': data.formulas.tyre_slip_torque,
    'Demand vs Slip Torque (Formula 32)': 'Compares T_demand = F_TW * r against T_slip',
  }

  return (
    <div>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
            Module D: FWD Traction & Gradeability (Formulas 22 – 32)
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Evaluates static axle loads, maximum front-wheel drive tractive force, 1st gear wheel spin, and gradeability.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onCalculate} disabled={isCalculating}>
          <Play size={15} fill="currentColor" />
          <span>Recalculate Module</span>
        </button>
      </div>

      <div className="comparison-container">
        {/* Case A: Kerb Mass */}
        <div className="case-card">
          <span className="case-badge case-badge-kerb">Kerb Mass Case</span>

          {kerb ? (
            <>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '14px 0 8px 0', color: 'var(--text-main)' }}>
                Axle Loads & Dynamic Transfer:
              </h4>
              <table className="calc-table">
                <tbody>
                  <tr>
                    <td>Static Front Axle Load (W_f)</td>
                    <td className="val-bold">{kerb.static_front_load_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Static Rear Axle Load (W_r)</td>
                    <td className="val-bold">{kerb.static_rear_load_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Longitudinal Load Transfer (ΔW)</td>
                    <td className="val-bold">{kerb.longitudinal_load_transfer_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td><strong>Dynamic Front Load (W_f,dyn)</strong></td>
                    <td className="val-bold">{kerb.dynamic_front_load_N.toFixed(2)} N</td>
                  </tr>
                </tbody>
              </table>

              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '20px 0 8px 0', color: 'var(--text-main)' }}>
                Traction Limit & 1st Gear Wheel Spin:
              </h4>
              <table className="calc-table">
                <tbody>
                  <tr>
                    <td>Max FWD Tractive Force (F_max)</td>
                    <td className="val-bold">{kerb.f_max_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>1st Gear Spin Condition</td>
                    <td>
                      <span className={`badge ${kerb.wheel_spin_1st_gear.spins ? 'badge-warning' : 'badge-success'}`}>
                        {kerb.wheel_spin_1st_gear.status}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td>Excess Force Beyond Grip</td>
                    <td className="val-bold">
                      {kerb.wheel_spin_1st_gear.excess_force_N > 0
                        ? `+${kerb.wheel_spin_1st_gear.excess_force_N.toFixed(1)} N`
                        : 'N/A (no spin)'}
                    </td>
                  </tr>
                  <tr>
                    <td>Tyre Slip Torque (T_slip)</td>
                    <td className="val-bold">{kerb.tyre_slip_torque_Nm.toFixed(2)} Nm</td>
                  </tr>
                  <tr>
                    <td>Wheel Torque Demand</td>
                    <td className="val-bold">
                      {kerb.torque_demand_vs_slip.wheel_torque_demand_Nm > 0
                        ? `${kerb.torque_demand_vs_slip.wheel_torque_demand_Nm.toFixed(2)} Nm`
                        : 'Unavailable'}
                    </td>
                  </tr>
                  <tr>
                    <td>Torque Demand vs Slip Check</td>
                    <td>
                      <span className="badge badge-warning">
                        {kerb.torque_demand_vs_slip.status}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>

              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '20px 0 8px 0', color: 'var(--text-main)' }}>
                Gradeability Limits:
              </h4>
              <table className="calc-table">
                <tbody>
                  <tr>
                    <td>Traction Factor (k = F_max / W)</td>
                    <td className="val-bold">{kerb.traction_factor_k.toFixed(4)}</td>
                  </tr>
                  <tr>
                    <td>Maximum Slope Angle (θ)</td>
                    <td className="val-bold">
                      {kerb.gradeability.gradeability_angle_deg.toFixed(2)}° ({kerb.gradeability.gradeability_angle_rad.toFixed(4)} rad)
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Maximum Gradient (G)</strong></td>
                    <td className="val-bold" style={{ color: '#0369a1' }}>
                      {kerb.gradeability.gradient_percent.toFixed(2)} %
                    </td>
                  </tr>
                </tbody>
              </table>
            </>
          ) : (
            <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Kerb mass traction analysis unavailable.</p>
          )}
        </div>

        {/* Case B: Gross Vehicle Mass */}
        <div className="case-card">
          <span className="case-badge case-badge-gvw">Gross Vehicle Mass Case</span>

          {gvw ? (
            <>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '14px 0 8px 0', color: 'var(--text-main)' }}>
                Axle Loads & Dynamic Transfer:
              </h4>
              <table className="calc-table">
                <tbody>
                  <tr>
                    <td>Static Front Axle Load (W_f)</td>
                    <td className="val-bold">{gvw.static_front_load_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Static Rear Axle Load (W_r)</td>
                    <td className="val-bold">{gvw.static_rear_load_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Longitudinal Load Transfer (ΔW)</td>
                    <td className="val-bold">{gvw.longitudinal_load_transfer_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td><strong>Dynamic Front Load (W_f,dyn)</strong></td>
                    <td className="val-bold">{gvw.dynamic_front_load_N.toFixed(2)} N</td>
                  </tr>
                </tbody>
              </table>

              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '20px 0 8px 0', color: 'var(--text-main)' }}>
                Traction Limit & 1st Gear Wheel Spin:
              </h4>
              <table className="calc-table">
                <tbody>
                  <tr>
                    <td>Max FWD Tractive Force (F_max)</td>
                    <td className="val-bold">{gvw.f_max_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>1st Gear Spin Condition</td>
                    <td>
                      <span className={`badge ${gvw.wheel_spin_1st_gear.spins ? 'badge-warning' : 'badge-success'}`}>
                        {gvw.wheel_spin_1st_gear.status}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td>Excess Force Beyond Grip</td>
                    <td className="val-bold">
                      {gvw.wheel_spin_1st_gear.excess_force_N > 0
                        ? `+${gvw.wheel_spin_1st_gear.excess_force_N.toFixed(1)} N`
                        : 'N/A (no spin)'}
                    </td>
                  </tr>
                  <tr>
                    <td>Tyre Slip Torque (T_slip)</td>
                    <td className="val-bold">{gvw.tyre_slip_torque_Nm.toFixed(2)} Nm</td>
                  </tr>
                  <tr>
                    <td>Wheel Torque Demand</td>
                    <td className="val-bold">
                      {gvw.torque_demand_vs_slip.wheel_torque_demand_Nm > 0
                        ? `${gvw.torque_demand_vs_slip.wheel_torque_demand_Nm.toFixed(2)} Nm`
                        : 'Unavailable'}
                    </td>
                  </tr>
                  <tr>
                    <td>Torque Demand vs Slip Check</td>
                    <td>
                      <span className="badge badge-warning">
                        {gvw.torque_demand_vs_slip.status}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>

              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '20px 0 8px 0', color: 'var(--text-main)' }}>
                Gradeability Limits:
              </h4>
              <table className="calc-table">
                <tbody>
                  <tr>
                    <td>Traction Factor (k = F_max / W)</td>
                    <td className="val-bold">{gvw.traction_factor_k.toFixed(4)}</td>
                  </tr>
                  <tr>
                    <td>Maximum Slope Angle (θ)</td>
                    <td className="val-bold">
                      {gvw.gradeability.gradeability_angle_deg.toFixed(2)}° ({gvw.gradeability.gradeability_angle_rad.toFixed(4)} rad)
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Maximum Gradient (G)</strong></td>
                    <td className="val-bold" style={{ color: '#0369a1' }}>
                      {gvw.gradeability.gradient_percent.toFixed(2)} %
                    </td>
                  </tr>
                </tbody>
              </table>
            </>
          ) : (
            <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Gross vehicle mass traction analysis unavailable.</p>
          )}
        </div>
      </div>

      <div className="card">
        <FormulaAccordion formulas={formulasRecord} />
      </div>
    </div>
  )
}
