import React from 'react'
import { Play } from 'lucide-react'
import type { BasicCalculationsOutput } from '../types'
import { FormulaAccordion } from '../components/FormulaAccordion'

interface BasicCalculationsViewProps {
  data: BasicCalculationsOutput | null
  onCalculate: () => void
  isCalculating: boolean
}

export const BasicCalculationsView: React.FC<BasicCalculationsViewProps> = ({
  data,
  onCalculate,
  isCalculating,
}) => {
  if (!data) {
    return (
      <div className="card">
        <p>No calculation results yet.</p>
        <button className="btn btn-primary" onClick={onCalculate} style={{ marginTop: 12 }}>
          Run Basic Calculations
        </button>
      </div>
    )
  }

  const formulasRecord: Record<string, string> = {
    'Free Tyre Radius (Formula 1)': data.free_tyre_radius.formula,
    'Dynamic Rolling Radius (Formula 2)': data.dynamic_rolling_radius.formula,
    'Vehicle Weight Kerb (Formula 3)': data.kerb_weight.formula,
    'Vehicle Weight GVW (Formula 3)': data.gross_vehicle_weight.formula,
    'Rated-Power Torque (Formula 5)': data.torque_at_rated_power.formula,
    'CG Distance Front L1 (Formula 6)': data.cg_distance_front_L1.formula,
    'CG Distance Rear L2 (Formula 6)': data.cg_distance_rear_L2.formula,
    'Overall Gear Ratios (Formula 4)': data.overall_gear_ratios.formula,
  }

  const gearRatios = (data.overall_gear_ratios.value as Record<string, number> | null) || null

  const renderRow = (label: string, item: any, digits: number = 2) => {
    const isAvail = item && item.value !== null && item.value !== undefined
    return (
      <tr>
        <td><strong>{label}</strong></td>
        <td className="val-bold">
          {isAvail ? Number(item.value).toFixed(digits) : (
            <span style={{ color: '#94a3b8', fontStyle: 'italic', fontWeight: 'normal' }}>N/A (unavailable)</span>
          )}
        </td>
        <td>{isAvail ? item.unit : '-'}</td>
        <td><code>{item.formula}</code></td>
      </tr>
    )
  }

  return (
    <div>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
            Module A: Basic Vehicle Calculations (Formulas 1 – 6)
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Computes tyre geometry under load, static weights, rated power torque, and CG longitudinal distances.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onCalculate} disabled={isCalculating}>
          <Play size={15} fill="currentColor" />
          <span>Recalculate Module</span>
        </button>
      </div>

      {/* Primary Results Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Calculated Vehicle Baseline Parameters</h3>
        </div>

        <div className="table-wrapper">
          <table className="calc-table">
            <thead>
              <tr>
                <th>Parameter Name</th>
                <th>Calculated Value</th>
                <th>Unit</th>
                <th>Formula / Expression</th>
              </tr>
            </thead>
            <tbody>
              {renderRow('Free Tyre Radius (r_free)', data.free_tyre_radius, 5)}
              {renderRow('Dynamic Rolling Radius (r)', data.dynamic_rolling_radius, 5)}
              {renderRow('Vehicle Weight — Kerb (W_kerb)', data.kerb_weight, 2)}
              {renderRow('Vehicle Weight — Fully Loaded (W_gvw)', data.gross_vehicle_weight, 2)}
              {renderRow('Torque at Rated Power (T_P)', data.torque_at_rated_power, 2)}
              {renderRow('CG Distance from Front Axle (L1)', data.cg_distance_front_L1, 4)}
              {renderRow('CG Distance from Rear Axle (L2)', data.cg_distance_rear_L2, 4)}
            </tbody>
          </table>
        </div>

        {/* Overall Gear Ratios Table */}
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, margin: '20px 0 10px 0', color: 'var(--text-main)' }}>
          Overall Transmission Ratios (io = ig × if)
        </h4>
        {gearRatios ? (
          <div className="table-wrapper">
            <table className="calc-table">
              <thead>
                <tr>
                  <th>Forward Gear</th>
                  <th>Overall Ratio (i_o)</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(gearRatios).map(([gear, ratio]) => (
                  <tr key={gear}>
                    <td><strong>Gear {gear}</strong></td>
                    <td className="val-bold">{Number(ratio).toFixed(4)}</td>
                    <td>Verified manufacturer ratio</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="alert-box alert-box-warning" style={{ margin: '10px 0 20px 0' }}>
            <span>Gear ratios unreleased by manufacturer for this profile. Enter custom ratios in Specifications to compute overall ratios.</span>
          </div>
        )}

        <FormulaAccordion formulas={formulasRecord} />
      </div>
    </div>
  )
}
