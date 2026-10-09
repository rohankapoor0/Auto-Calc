import React from 'react'
import { Play, AlertCircle } from 'lucide-react'
import type { AWDOutput } from '../types'
import { FormulaAccordion } from '../components/FormulaAccordion'

interface AWDViewProps {
  data: AWDOutput | null
  isSupported?: boolean
  vehicleName?: string
  onCalculateAWD: () => void
  isCalculating: boolean
}

export const AWDView: React.FC<AWDViewProps> = ({
  data,
  isSupported = true,
  vehicleName = 'Hyundai Creta',
  onCalculateAWD,
  isCalculating,
}) => {
  if (!isSupported) {
    return (
      <div className="card" style={{ padding: '36px 24px', textAlign: 'center' }}>
        <div className="badge badge-warning" style={{ marginBottom: 12 }}>
          Analysis Disabled
        </div>
        <h3 style={{ fontSize: '1.2rem', marginBottom: 10, color: 'var(--accent-primary)' }}>
          AWD Analysis Not Applicable for {vehicleName}
        </h3>
        <p style={{ color: 'var(--text-muted)', maxWidth: 640, margin: '0 auto 20px auto', fontSize: '0.9rem' }}>
          This vehicle is strictly Front-Wheel Drive (FWD). The hypothetical AWD extension was formulated specifically
          as an academic design study in the Hyundai Creta Design Dossier (Pages 9–10).
          To avoid mixing unverified AWD kinematic models into standard production vehicles, this module is kept separate and disabled.
        </p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="card" style={{ padding: '36px 24px', textAlign: 'center' }}>
        <div className="badge badge-warning" style={{ marginBottom: 12 }}>
          Hypothetical Analysis Study
        </div>
        <h3 style={{ fontSize: '1.2rem', marginBottom: 10, color: 'var(--accent-primary)' }}>
          Hypothetical All-Wheel Drive (AWD) Extension
        </h3>
        <p style={{ color: 'var(--text-muted)', maxWidth: 640, margin: '0 auto 20px auto', fontSize: '0.9rem' }}>
          The production Hyundai Creta is Front-Wheel Drive (FWD). Pages 9–10 of the design dossier explore a hypothetical
          all-wheel drive cornering analysis under tight turning conditions (Ro = 5.3 m, track = 1.55 m).
        </p>
        <button className="btn btn-primary" onClick={onCalculateAWD} disabled={isCalculating}>
          <Play size={15} fill="currentColor" />
          <span>Execute Hypothetical AWD Analysis</span>
        </button>
      </div>
    )
  }

  const kerb = data.kerb_mass
  const kin = kerb.kinematics
  const dyn = kerb.dynamics
  const diff = kerb.differential_comparison

  const formulasRecord: Record<string, string> = {
    'Rear Axle Centre Radius (Formula 44)': 'R_r = sqrt(R_o^2 - L^2) - (t / 2)',
    'Front Inner Radius (Formula 45)': 'R_FI = sqrt((R_r - t/2)^2 + L^2)',
    'Rear Outer Radius (Formula 46)': 'R_RO = sqrt(R_r^2 + L^2)',
    'Rear Inner Radius (Formula 47)': 'R_RI = R_r - (t / 2)',
    'Outer Steering Angle (Formula 48)': 'delta_o = atan(L / R_r)',
    'Inner Steering Angle (Formula 49)': 'delta_i = atan(L / (R_r - t/2))',
    'CG Turning Radius (Formula 50)': 'R_CG = sqrt(R_r^2 + L_2^2)',
    'Yaw Rate (Formula 51)': 'Omega = V / R_CG',
    'Wheel Rotational Speed (Formula 52)': 'N_w = Omega * (R_w / r) * (60 / (2*pi))',
    'Lateral Acceleration (Formula 53)': 'a_y = V^2 / R_CG',
    'Lateral Load Transfer Factor (Formula 54)': 'lambda = (a_y / g) * (h / t)',
    'Axle Lateral Transfers (Formulas 55-56)': 'Delta_F_zf = W_f * lambda, Delta_F_zr = W_r * lambda',
    'Individual Wheel Loads (Formulas 57-60)': 'FO/FI = (W_f / 2) ± Delta_F_zf, RO/RI = (W_r / 2) ± Delta_F_zr',
    'Lateral Force per Wheel (Formula 61)': 'F_y = F_z * (a_y / g)',
    'Remaining Friction Coefficient (Formula 62)': 'mu_x = sqrt(mu^2 - (a_y / g)^2)',
    'Maximum Torque per Wheel (Formula 64)': 'T_max = eta * mu_x * F_z * r (eta = 1)',
    'Open Differential Configuration (Formula 66)': 'T_open = 4 * min(T_FO, T_FI, T_RO, T_RI)',
    'Fixed 60:40 Centre Differential (Formula 67)': 'T_rear = 2*min(RO, RI), T_total = T_rear / 0.40',
    'Locked Centre Differential (Formula 68)': 'T_locked = 2*min(FO, FI) + 2*min(RO, RI)',
    'Ideal Torque-Vectoring (Formula 69)': 'T_ideal = T_FO + T_FI + T_RO + T_RI',
  }

  return (
    <div>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
              Module F: Hypothetical AWD Extension (Formulas 44 – 70)
            </h2>
            <span className="badge badge-warning">Hypothetical Study Only</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Cornering kinematics, friction circle limits, and torque distribution across differential architectures.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onCalculateAWD} disabled={isCalculating}>
          <Play size={15} fill="currentColor" />
          <span>Recalculate AWD Module</span>
        </button>
      </div>

      <div className="alert-box alert-box-warning">
        <AlertCircle size={20} />
        <div>
          <strong>Engineering Note:</strong> The production Creta 1.5 CRDi is strictly front-wheel drive. This analysis
          reflects pages 9–10 of the design dossier, modeling hypothetical torque vectoring and differential limits under
          cornering at 3.32 m/s with an outer turning radius of 5.3 m and track width of 1.55 m.
        </div>
      </div>

      {/* Differential Layout Comparison (Key Findings) */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Centre Differential Torque Capacity Comparison (Kerb Mass)</h3>
        </div>

        <div className="table-wrapper">
          <table className="calc-table">
            <thead>
              <tr>
                <th>Configuration</th>
                <th>Total Usable Torque</th>
                <th>Percentage of Ideal</th>
                <th>Operating Constraint</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>1. Ideal Torque-Vectoring AWD</strong></td>
                <td className="val-bold" style={{ color: '#166534' }}>
                  {diff.torque_vectoring_ideal.total_torque_Nm.toFixed(1)} Nm
                </td>
                <td>
                  <span className="badge badge-success">100.0 %</span>
                </td>
                <td>Full independent wheel slip utilization</td>
              </tr>
              <tr>
                <td><strong>2. Locked Centre Diff (Open Front & Rear)</strong></td>
                <td className="val-bold">{diff.locked_center_differential.total_torque_Nm.toFixed(1)} Nm</td>
                <td>
                  <span className="badge badge-success">
                    {diff.locked_center_differential.percentage_of_ideal.toFixed(1)} %
                  </span>
                </td>
                <td>Axles locked; each axle limited by inner wheel</td>
              </tr>
              <tr>
                <td><strong>3. Fixed 60:40 Centre Differential</strong></td>
                <td className="val-bold">{diff.fixed_60_40_center_differential.total_torque_Nm.toFixed(1)} Nm</td>
                <td>
                  <span className="badge badge-warning">
                    {diff.fixed_60_40_center_differential.percentage_of_ideal.toFixed(1)} %
                  </span>
                </td>
                <td>Rear axle limits overall torque (40% allocation)</td>
              </tr>
              <tr>
                <td><strong>4. Fully Open Differentials (All 3 Open)</strong></td>
                <td className="val-bold" style={{ color: '#b91c1c' }}>
                  {diff.open_differential.total_torque_Nm.toFixed(1)} Nm
                </td>
                <td>
                  <span className="badge badge-danger">
                    {diff.open_differential.percentage_of_ideal.toFixed(1)} %
                  </span>
                </td>
                <td>Limited to 4× the weakest wheel (Rear Inner)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Kinematics and Cornering Normal Loads */}
      <div className="comparison-container">
        {/* Kinematics */}
        <div className="case-card">
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-main)' }}>
            Kinematic Geometry & Wheel Speeds (V = 3.32 m/s):
          </h4>
          <table className="calc-table">
            <tbody>
              <tr>
                <td>Rear Axle Center Radius (R_r)</td>
                <td className="val-bold">{kin.R_rear_m.toFixed(3)} m</td>
              </tr>
              <tr>
                <td>Front Inner Wheel Radius (R_FI)</td>
                <td className="val-bold">{kin.R_FI_m.toFixed(3)} m</td>
              </tr>
              <tr>
                <td>Rear Outer Wheel Radius (R_RO)</td>
                <td className="val-bold">{kin.R_RO_m.toFixed(3)} m</td>
              </tr>
              <tr>
                <td>Rear Inner Wheel Radius (R_RI)</td>
                <td className="val-bold">{kin.R_RI_m.toFixed(3)} m</td>
              </tr>
              <tr>
                <td>CG Turning Radius (R_CG)</td>
                <td className="val-bold">{kin.R_CG_m.toFixed(3)} m</td>
              </tr>
              <tr>
                <td>Outer Steering Angle (δ_o)</td>
                <td className="val-bold">{kin.delta_outer_deg.toFixed(2)}°</td>
              </tr>
              <tr>
                <td>Inner Steering Angle (δ_i)</td>
                <td className="val-bold">{kin.delta_inner_deg.toFixed(2)}°</td>
              </tr>
              <tr>
                <td>Vehicle Yaw Rate (Ω)</td>
                <td className="val-bold">{kin.yaw_rate_rad_s.toFixed(4)} rad/s</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Dynamic Loads & Remaining Grip */}
        <div className="case-card">
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-main)' }}>
            Cornering Dynamics & Normal Wheel Loads:
          </h4>
          <table className="calc-table">
            <tbody>
              <tr>
                <td>Lateral Acceleration (a_y)</td>
                <td className="val-bold">{dyn.lateral_acceleration_m_s2.toFixed(3)} m/s²</td>
              </tr>
              <tr>
                <td>Lateral Load Transfer Factor (λ)</td>
                <td className="val-bold">{dyn.lateral_load_transfer_factor_lambda.toFixed(4)}</td>
              </tr>
              <tr>
                <td>Remaining Friction Coeff (μ_x)</td>
                <td className="val-bold">{dyn.remaining_mu_x.toFixed(4)}</td>
              </tr>
              <tr>
                <td>Front Outer Wheel Load (F_z,FO)</td>
                <td className="val-bold">{dyn.wheel_vertical_loads_N['F_z_FO']?.toFixed(1)} N</td>
              </tr>
              <tr>
                <td>Front Inner Wheel Load (F_z,FI)</td>
                <td className="val-bold">{dyn.wheel_vertical_loads_N['F_z_FI']?.toFixed(1)} N</td>
              </tr>
              <tr>
                <td>Rear Outer Wheel Load (F_z,RO)</td>
                <td className="val-bold">{dyn.wheel_vertical_loads_N['F_z_RO']?.toFixed(1)} N</td>
              </tr>
              <tr>
                <td>Rear Inner Wheel Load (F_z,RI)</td>
                <td className="val-bold">{dyn.wheel_vertical_loads_N['F_z_RI']?.toFixed(1)} N</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <FormulaAccordion formulas={formulasRecord} />
      </div>
    </div>
  )
}
