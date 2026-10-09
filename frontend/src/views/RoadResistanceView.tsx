import React from 'react'
import { Play } from 'lucide-react'
import type { RoadResistanceOutput } from '../types'
import { FormulaAccordion } from '../components/FormulaAccordion'

interface RoadResistanceViewProps {
  data: RoadResistanceOutput | null
  onCalculate: () => void
  isCalculating: boolean
}

export const RoadResistanceView: React.FC<RoadResistanceViewProps> = ({
  data,
  onCalculate,
  isCalculating,
}) => {
  if (!data) {
    return (
      <div className="card">
        <p>No road resistance calculations available yet.</p>
        <button className="btn btn-primary" onClick={onCalculate} style={{ marginTop: 12 }}>
          Run Road Resistance Analysis
        </button>
      </div>
    )
  }

  const kConstant = data.air_resistance_constant.value !== null ? Number(data.air_resistance_constant.value) : null
  const kerb = data.kerb_mass
  const gvw = data.gross_vehicle_mass

  const formulasRecord: Record<string, string> = {
    'Air Resistance Constant (Formula 11)': data.air_resistance_constant.formula,
    'Rolling Resistance (Formula 12)': 'R_RR = f_r * W',
    'Aerodynamic Drag (Formula 13)': 'R_AF = 0.5 * rho * C_D * A * V^2 = k * V^2',
    'Grade Resistance (Formula 14)': 'R_GR = W * sin(theta) (Level road: theta=0, R_GR=0)',
    'Total Road Resistance (Formula 15)': 'R_T = R_RR + R_AF + R_GR',
    'Drawbar Pull / Spare Force (Formula 16)': 'F_db = F_TW - R_T',
    'Wheel Power (Formula 17)': 'P_wheel = R_T * V (kW = W / 1000)',
    'Engine Power (Formula 18)': 'P_engine = P_wheel / eta_T',
    'Engine Speed from Road Speed (Formula 19)': 'N_engine = (V / r) * (60 / (2*pi)) * i_o',
    'Top-Speed Feasibility (Formula 20)':
      'Evaluates F_TW vs R_T at rated RPM in top gear to check spare tractive force.',
    'Power at 100 km/h (Formula 21)': 'Fixed velocity V = 100 / 3.6 m/s',
  }

  return (
    <div>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
            Module C: Road Resistance & Power Demands (Formulas 11 – 21)
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Computes rolling resistance, aerodynamic drag, power required at 100 km/h, and top-speed feasibility.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onCalculate} disabled={isCalculating}>
          <Play size={15} fill="currentColor" />
          <span>Recalculate Module</span>
        </button>
      </div>

      {/* Aerodynamic Constant Card */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 12 }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
            AERODYNAMIC RESISTANCE CONSTANT:
          </div>
          <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
            {kConstant !== null ? `k = ${kConstant.toFixed(4)}` : 'N/A'}{' '}
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>kg/m</span>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            (Formula: <code>k = 0.5 × ρ × CD × A</code>)
          </div>
        </div>
      </div>

      {/* Two Cases Comparison Tables */}
      <div className="comparison-container">
        {/* Case A: Kerb Mass */}
        <div className="case-card">
          <span className="case-badge case-badge-kerb">
            Kerb Mass {kerb ? `(${kerb.weight_N.toFixed(1)} N)` : ''}
          </span>

          {kerb ? (
            <>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '14px 0 8px 0', color: 'var(--text-main)' }}>
                Power Demand at 100 km/h (27.78 m/s):
              </h4>
              <table className="calc-table">
                <tbody>
                  <tr>
                    <td>Rolling Resistance (R_RR)</td>
                    <td className="val-bold">{kerb.power_at_100kmh.rolling_resistance_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Aerodynamic Resistance (R_AF)</td>
                    <td className="val-bold">{kerb.power_at_100kmh.aerodynamic_resistance_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Total Resistance (R_T)</td>
                    <td className="val-bold">{kerb.power_at_100kmh.total_resistance_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Wheel Power Required</td>
                    <td className="val-bold">{kerb.power_at_100kmh.wheel_power_kw.toFixed(2)} kW</td>
                  </tr>
                  <tr>
                    <td><strong>Engine Power Required (ηT = 0.90)</strong></td>
                    <td className="val-bold" style={{ color: '#166534' }}>
                      {kerb.power_at_100kmh.engine_power_kw.toFixed(2)} kW
                    </td>
                  </tr>
                </tbody>
              </table>

              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '20px 0 8px 0', color: 'var(--text-main)' }}>
                Top Speed Feasibility Check (Top Gear @ Rated RPM):
              </h4>
              {kerb.top_speed_check_6th_gear ? (
                <table className="calc-table">
                  <tbody>
                    <tr>
                      <td>Rated Vehicle Speed</td>
                      <td className="val-bold">{kerb.top_speed_check_6th_gear.rated_speed_kmh.toFixed(2)} km/h</td>
                    </tr>
                    <tr>
                      <td>Available Tractive Effort (F_TW)</td>
                      <td className="val-bold">{kerb.top_speed_check_6th_gear.tractive_effort_N.toFixed(1)} N</td>
                    </tr>
                    <tr>
                      <td>Total Road Resistance (R_T)</td>
                      <td className="val-bold">{kerb.top_speed_check_6th_gear.total_resistance_N.toFixed(1)} N</td>
                    </tr>
                    <tr>
                      <td>Spare Force (Drawbar Pull)</td>
                      <td className="val-bold">+{kerb.top_speed_check_6th_gear.spare_force_drawbar_pull_N.toFixed(1)} N</td>
                    </tr>
                    <tr>
                      <td>Feasibility Status</td>
                      <td>
                        <span className="badge badge-success">
                          {kerb.top_speed_check_6th_gear.feasibility_status}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              ) : (
                <p style={{ color: '#94a3b8', fontSize: '0.825rem', marginTop: 8 }}>
                  Top-speed calculation unavailable: requires verified gear ratios and final drive.
                </p>
              )}
            </>
          ) : (
            <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Kerb mass calculation unavailable.</p>
          )}
        </div>

        {/* Case B: Gross Vehicle Mass */}
        <div className="case-card">
          <span className="case-badge case-badge-gvw">
            Gross Vehicle Mass {gvw ? `(${gvw.weight_N.toFixed(1)} N)` : ''}
          </span>

          {gvw ? (
            <>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '14px 0 8px 0', color: 'var(--text-main)' }}>
                Power Demand at 100 km/h (27.78 m/s):
              </h4>
              <table className="calc-table">
                <tbody>
                  <tr>
                    <td>Rolling Resistance (R_RR)</td>
                    <td className="val-bold">{gvw.power_at_100kmh.rolling_resistance_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Aerodynamic Resistance (R_AF)</td>
                    <td className="val-bold">{gvw.power_at_100kmh.aerodynamic_resistance_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Total Resistance (R_T)</td>
                    <td className="val-bold">{gvw.power_at_100kmh.total_resistance_N.toFixed(2)} N</td>
                  </tr>
                  <tr>
                    <td>Wheel Power Required</td>
                    <td className="val-bold">{gvw.power_at_100kmh.wheel_power_kw.toFixed(2)} kW</td>
                  </tr>
                  <tr>
                    <td><strong>Engine Power Required (ηT = 0.90)</strong></td>
                    <td className="val-bold" style={{ color: '#166534' }}>
                      {gvw.power_at_100kmh.engine_power_kw.toFixed(2)} kW
                    </td>
                  </tr>
                </tbody>
              </table>

              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '20px 0 8px 0', color: 'var(--text-main)' }}>
                Top Speed Feasibility Check (Top Gear @ Rated RPM):
              </h4>
              {gvw.top_speed_check_6th_gear ? (
                <table className="calc-table">
                  <tbody>
                    <tr>
                      <td>Rated Vehicle Speed</td>
                      <td className="val-bold">{gvw.top_speed_check_6th_gear.rated_speed_kmh.toFixed(2)} km/h</td>
                    </tr>
                    <tr>
                      <td>Available Tractive Effort (F_TW)</td>
                      <td className="val-bold">{gvw.top_speed_check_6th_gear.tractive_effort_N.toFixed(1)} N</td>
                    </tr>
                    <tr>
                      <td>Total Road Resistance (R_T)</td>
                      <td className="val-bold">{gvw.top_speed_check_6th_gear.total_resistance_N.toFixed(1)} N</td>
                    </tr>
                    <tr>
                      <td>Spare Force (Drawbar Pull)</td>
                      <td className="val-bold">+{gvw.top_speed_check_6th_gear.spare_force_drawbar_pull_N.toFixed(1)} N</td>
                    </tr>
                    <tr>
                      <td>Feasibility Status</td>
                      <td>
                        <span className="badge badge-success">
                          {gvw.top_speed_check_6th_gear.feasibility_status}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              ) : (
                <p style={{ color: '#94a3b8', fontSize: '0.825rem', marginTop: 8 }}>
                  Top-speed calculation unavailable: requires verified gear ratios and final drive.
                </p>
              )}
            </>
          ) : (
            <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Gross vehicle mass unavailable.</p>
          )}
        </div>
      </div>

      <div className="card">
        <FormulaAccordion formulas={formulasRecord} />
      </div>
    </div>
  )
}
