import React from 'react'
import { Play, AlertCircle } from 'lucide-react'
import type { ClutchOutput } from '../types'
import { FormulaAccordion } from '../components/FormulaAccordion'

interface ClutchViewProps {
  data: ClutchOutput | null
  onCalculate: () => void
  isCalculating: boolean
}

export const ClutchView: React.FC<ClutchViewProps> = ({
  data,
  onCalculate,
  isCalculating,
}) => {
  if (!data) {
    return (
      <div className="card">
        <p>No clutch design calculations available yet.</p>
        <button className="btn btn-primary" onClick={onCalculate} style={{ marginTop: 12 }}>
          Run Clutch Analysis
        </button>
      </div>
    )
  }

  const c = data.results

  const formulasRecord: Record<string, string> = {
    'Outer Friction Radius (Formula 33)': data.formulas.outer_radius,
    'Inner Friction Radius (Formula 34)': data.formulas.inner_radius,
    'Mean Friction Radius (Formula 35)': data.formulas.mean_radius,
    'Design Torque (Formula 36)': data.formulas.design_torque,
    'Axial Clamping Force (Formula 37)': data.formulas.axial_clamping_force,
    'Effective Radius Uniform Pressure (Formula 38)': data.formulas.effective_radius,
    'Torque Capacity Uniform Pressure (Formula 39)': data.formulas.torque_capacity_uniform_pressure,
    'Average Contact Pressure (Formula 40)': data.formulas.average_contact_pressure,
    'Uniform Wear Constant (Formula 41)': data.formulas.uniform_wear_constant,
    'Max Pressure Uniform Wear (Formula 42)': data.formulas.max_pressure_uniform_wear,
    'Min Pressure Uniform Wear (Formula 43)': data.formulas.min_pressure_uniform_wear,
  }

  return (
    <div>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
            Module E: Clutch Design & Contact Pressure Analysis (Formulas 33 – 43)
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Evaluates dry clutch plate dimensions, design torque capacity, axial clamping force, and contact pressure distribution.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onCalculate} disabled={isCalculating}>
          <Play size={15} fill="currentColor" />
          <span>Recalculate Module</span>
        </button>
      </div>

      {!c ? (
        <div className="card">
          <div className="alert-box alert-box-warning">
            <AlertCircle size={20} />
            <div>
              <strong>Calculations Incomplete:</strong> {data.note || 'Clutch plate dimensions (OD/ID) are proprietary service data not published by the manufacturer for this vehicle.'}
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            To preserve engineering integrity, clutch dimensions from other car models are not automatically substituted.
            You can input verified dimensions under the <strong>Specifications</strong> tab to compute clamping force and contact stresses.
          </p>
        </div>
      ) : (
        <>
          {/* Primary Metrics Grid */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Design Torque (Tc)</div>
              <div className="metric-value-wrap">
                <span className="metric-val">{c.design_torque_Tc_Nm.toFixed(1)}</span>
                <span className="metric-unit">Nm</span>
              </div>
              <div className="metric-sub">SF = 1.25 × Te</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Axial Clamping Force (Wc)</div>
              <div className="metric-value-wrap">
                <span className="metric-val">{c.axial_clamping_force_Wc_N.toFixed(1)}</span>
                <span className="metric-unit">N</span>
              </div>
              <div className="metric-sub">Uniform Wear Model</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Uniform Pressure Torque</div>
              <div className="metric-value-wrap">
                <span className="metric-val">{c.torque_capacity_uniform_pressure_Nm.toFixed(1)}</span>
                <span className="metric-unit">Nm</span>
              </div>
              <div className="metric-sub">Using R_eff ({(c.effective_radius_Reff_m * 1000).toFixed(1)} mm)</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Average Pressure (p_avg)</div>
              <div className="metric-value-wrap">
                <span className="metric-val">{c.average_contact_pressure_MPa.toFixed(4)}</span>
                <span className="metric-unit">MPa</span>
              </div>
              <div className="metric-sub">{c.average_contact_pressure_Pa.toFixed(0)} Pa</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Max Pressure (p_max)</div>
              <div className="metric-value-wrap">
                <span className="metric-val">{c.max_pressure_uniform_wear_MPa.toFixed(4)}</span>
                <span className="metric-unit">MPa</span>
              </div>
              <div className="metric-sub">At Inner Radius (r2)</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Min Pressure (p_min)</div>
              <div className="metric-value-wrap">
                <span className="metric-val">{c.min_pressure_uniform_wear_MPa.toFixed(4)}</span>
                <span className="metric-unit">MPa</span>
              </div>
              <div className="metric-sub">At Outer Radius (r1)</div>
            </div>
          </div>

          {/* Detailed Geometry and Pressure Table */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Detailed Clutch Friction & Mechanics Results</h3>
            </div>

            <div className="table-wrapper">
              <table className="calc-table">
                <thead>
                  <tr>
                    <th>Parameter</th>
                    <th>Symbol</th>
                    <th>Calculated Value</th>
                    <th>Unit</th>
                    <th>Engineering Significance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Outer Friction Radius</td>
                    <td><code>r_1</code></td>
                    <td className="val-bold">{(c.outer_radius_r1_m * 1000).toFixed(1)}</td>
                    <td>mm</td>
                    <td>OD / 2</td>
                  </tr>
                  <tr>
                    <td>Inner Friction Radius</td>
                    <td><code>r_2</code></td>
                    <td className="val-bold">{(c.inner_radius_r2_m * 1000).toFixed(1)}</td>
                    <td>mm</td>
                    <td>ID / 2</td>
                  </tr>
                  <tr>
                    <td>Mean Friction Radius</td>
                    <td><code>R</code></td>
                    <td className="val-bold">{(c.mean_radius_R_m * 1000).toFixed(2)}</td>
                    <td>mm</td>
                    <td>Arithmetic mean of r1 and r2</td>
                  </tr>
                  <tr>
                    <td>Effective Radius (Uniform Pressure)</td>
                    <td><code>R_eff</code></td>
                    <td className="val-bold">{(c.effective_radius_Reff_m * 1000).toFixed(2)}</td>
                    <td>mm</td>
                    <td>(2/3) × (r1³ - r2³) / (r1² - r2²)</td>
                  </tr>
                  <tr>
                    <td>Design Torque Margin</td>
                    <td><code>T_c</code></td>
                    <td className="val-bold">{c.design_torque_Tc_Nm.toFixed(2)}</td>
                    <td>Nm</td>
                    <td>Engine torque multiplied by 1.25 safety factor</td>
                  </tr>
                  <tr>
                    <td>Axial Clamping Force (Diaphragm Spring)</td>
                    <td><code>W_c</code></td>
                    <td className="val-bold">{c.axial_clamping_force_Wc_N.toFixed(2)}</td>
                    <td>N</td>
                    <td>Required normal force under uniform wear</td>
                  </tr>
                  <tr>
                    <td>Uniform Wear Constant</td>
                    <td><code>C</code></td>
                    <td className="val-bold">{c.uniform_wear_constant_C_Npm.toFixed(2)}</td>
                    <td>N/m</td>
                    <td>C = W_c / (2π(r1 - r2))</td>
                  </tr>
                  <tr>
                    <td>Average Contact Pressure</td>
                    <td><code>p_avg</code></td>
                    <td className="val-bold">{c.average_contact_pressure_MPa.toFixed(4)}</td>
                    <td>MPa</td>
                    <td>Total axial force divided by annular friction area</td>
                  </tr>
                  <tr>
                    <td>Maximum Contact Pressure (at r2)</td>
                    <td><code>p_max</code></td>
                    <td className="val-bold">{c.max_pressure_uniform_wear_MPa.toFixed(4)}</td>
                    <td>MPa</td>
                    <td>Peak contact stress on clutch lining</td>
                  </tr>
                  <tr>
                    <td>Minimum Contact Pressure (at r1)</td>
                    <td><code>p_min</code></td>
                    <td className="val-bold">{c.min_pressure_uniform_wear_MPa.toFixed(4)}</td>
                    <td>MPa</td>
                    <td>Trailing edge contact stress</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <FormulaAccordion formulas={formulasRecord} />
          </div>
        </>
      )}
    </div>
  )
}
