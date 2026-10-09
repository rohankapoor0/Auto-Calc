import React from 'react'
import { Play, ArrowRight } from 'lucide-react'
import type { FullVehicleCalculationResponse, VehicleProfile } from '../types'
import type { NavSection } from '../components/Sidebar'
import { VehicleSummary } from '../components/VehicleSummary'

interface OverviewViewProps {
  results: FullVehicleCalculationResponse | null
  profile?: VehicleProfile
  onCalculateAll: () => void
  isCalculating: boolean
  onNavigate: (section: NavSection) => void
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  results,
  profile,
  onCalculateAll,
  isCalculating,
  onNavigate,
}) => {
  if (!results) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '48px 24px' }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: 12, color: 'var(--accent-primary)' }}>
          AutoCalc Engine Ready
        </h3>
        <p style={{ color: 'var(--text-muted)', marginBottom: 24, maxWidth: 500, margin: '0 auto 24px auto' }}>
          Execute the Python calculation engine for {profile ? `${profile.manufacturer} ${profile.name}` : 'the selected vehicle'}.
        </p>
        <button className="btn btn-primary" onClick={onCalculateAll} disabled={isCalculating}>
          <Play size={16} fill="currentColor" />
          <span>Calculate All Modules Now</span>
        </button>
      </div>
    )
  }

  const basic = results.basic_calculations
  const drive = results.drivetrain
  const road = results.road_resistance
  const trac = results.traction
  const clutch = results.clutch.results

  const rFree = basic.free_tyre_radius.value !== null ? Number(basic.free_tyre_radius.value) : null
  const rDyn = basic.dynamic_rolling_radius.value !== null ? Number(basic.dynamic_rolling_radius.value) : null
  const tRated = basic.torque_at_rated_power.value !== null ? Number(basic.torque_at_rated_power.value) : null
  const wKerb = basic.kerb_weight.value !== null ? Number(basic.kerb_weight.value) : null
  const wGvw = basic.gross_vehicle_weight.value !== null ? Number(basic.gross_vehicle_weight.value) : null

  const ftw1st = drive.status === 'calculated' && drive.gears['1'] ? drive.gears['1'].tractive_effort_plateau_N : null
  const topSpeedKerb = road.kerb_mass?.top_speed_check_6th_gear?.rated_speed_kmh ?? null
  const clutchTc = clutch ? clutch.design_torque_Tc_Nm : null

  return (
    <div>
      {/* Vehicle Summary Header Card */}
      {profile && <VehicleSummary profile={profile} />}

      {/* Action Banner */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
            Engineering Performance Summary
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Direct Python physics execution — Indian market compact SUV benchmarking.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onCalculateAll} disabled={isCalculating}>
          <Play size={15} fill="currentColor" />
          <span>Recalculate Profile</span>
        </button>
      </div>

      {/* Primary KPI Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Free Tyre Radius</div>
          <div className="metric-value-wrap">
            <span className="metric-val">{rFree !== null ? rFree.toFixed(5) : 'N/A'}</span>
            {rFree !== null && <span className="metric-unit">m</span>}
          </div>
          <div className="metric-sub">{profile?.tyres.tyre_spec.value || 'r_free'}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Dynamic Rolling Radius</div>
          <div className="metric-value-wrap">
            <span className="metric-val">{rDyn !== null ? rDyn.toFixed(5) : 'N/A'}</span>
            {rDyn !== null && <span className="metric-unit">m</span>}
          </div>
          <div className="metric-sub">r = 0.97 × r_free</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Rated-Power Torque</div>
          <div className="metric-value-wrap">
            <span className="metric-val">{tRated !== null ? tRated.toFixed(2) : 'N/A'}</span>
            {tRated !== null && <span className="metric-unit">Nm</span>}
          </div>
          <div className="metric-sub">
            {profile?.engine.max_power_kw.value} kW @ {profile?.engine.rated_power_rpm.value} rpm
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">1st Gear Tractive Effort</div>
          <div className="metric-value-wrap">
            <span className="metric-val" style={ftw1st === null ? { fontSize: '1.05rem', color: '#64748b' } : {}}>
              {ftw1st !== null ? ftw1st.toFixed(1) : 'Gear ratios unreleased'}
            </span>
            {ftw1st !== null && <span className="metric-unit">N</span>}
          </div>
          <div className="metric-sub">
            {ftw1st !== null ? 'F_TW @ torque peak' : 'Proprietary service data'}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Theoretical Top Speed</div>
          <div className="metric-value-wrap">
            <span className="metric-val" style={topSpeedKerb === null ? { fontSize: '1.05rem', color: '#64748b' } : {}}>
              {topSpeedKerb !== null ? topSpeedKerb.toFixed(1) : 'Gear ratios unreleased'}
            </span>
            {topSpeedKerb !== null && <span className="metric-unit">km/h</span>}
          </div>
          <div className="metric-sub">
            {topSpeedKerb !== null ? 'Top gear @ rated rpm' : 'Unavailable'}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Clutch Design Torque</div>
          <div className="metric-value-wrap">
            <span className="metric-val" style={clutchTc === null ? { fontSize: '1.05rem', color: '#64748b' } : {}}>
              {clutchTc !== null ? clutchTc.toFixed(1) : 'Clutch dims unreleased'}
            </span>
            {clutchTc !== null && <span className="metric-unit">Nm</span>}
          </div>
          <div className="metric-sub">
            {clutchTc !== null ? 'T_c = 1.25 × T_e' : 'Proprietary service data'}
          </div>
        </div>
      </div>

      {/* Two Load Cases Comparison */}
      <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-main)' }}>
        Two Load Cases Comparison: Kerb Mass vs Fully Loaded (GVW)
      </h3>

      <div className="comparison-container">
        {/* Case A: Kerb Mass */}
        <div className="case-card">
          <span className="case-badge case-badge-kerb">
            Case A: Kerb Mass ({profile?.weights.kerb_mass_kg.value ?? 'N/A'} kg)
          </span>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--accent-primary)', marginBottom: 12 }}>
            {wKerb !== null ? wKerb.toFixed(1) : 'N/A'}{' '}
            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>N</span>
          </div>

          <table className="calc-table" style={{ marginTop: 8 }}>
            <tbody>
              <tr>
                <td>Static Front Axle Load (W_f)</td>
                <td className="val-bold">
                  {trac.kerb_mass ? `${trac.kerb_mass.static_front_load_N.toFixed(1)} N` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>Static Rear Axle Load (W_r)</td>
                <td className="val-bold">
                  {trac.kerb_mass ? `${trac.kerb_mass.static_rear_load_N.toFixed(1)} N` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>Max FWD Tractive Force (F_max)</td>
                <td className="val-bold">
                  {trac.kerb_mass ? `${trac.kerb_mass.f_max_N.toFixed(1)} N` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>1st Gear Wheel Spin Check</td>
                <td>
                  {trac.kerb_mass ? (
                    <span className={`badge ${trac.kerb_mass.wheel_spin_1st_gear.spins ? 'badge-warning' : 'badge-success'}`}>
                      {trac.kerb_mass.wheel_spin_1st_gear.status}
                    </span>
                  ) : (
                    'N/A'
                  )}
                </td>
              </tr>
              <tr>
                <td>Road Resistance @ 100 km/h</td>
                <td className="val-bold">
                  {road.kerb_mass ? `${road.kerb_mass.power_at_100kmh.total_resistance_N.toFixed(1)} N` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>Engine Power Req. @ 100 km/h</td>
                <td className="val-bold">
                  {road.kerb_mass ? `${road.kerb_mass.power_at_100kmh.engine_power_kw.toFixed(2)} kW` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>Top-Speed Spare Force (Drawbar Pull)</td>
                <td>
                  {road.kerb_mass?.top_speed_check_6th_gear ? (
                    <span className="badge badge-success">
                      +{road.kerb_mass.top_speed_check_6th_gear.spare_force_drawbar_pull_N.toFixed(1)} N
                    </span>
                  ) : (
                    <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>
                      N/A (gear ratios unreleased)
                    </span>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Case B: Gross Vehicle Mass */}
        <div className="case-card">
          <span className="case-badge case-badge-gvw">
            Case B: Fully Loaded GVW ({profile?.weights.gross_vehicle_mass_kg.value ?? 'N/A'} kg)
          </span>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--accent-primary)', marginBottom: 12 }}>
            {wGvw !== null ? wGvw.toFixed(1) : 'N/A'}{' '}
            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>N</span>
          </div>

          <table className="calc-table" style={{ marginTop: 8 }}>
            <tbody>
              <tr>
                <td>Static Front Axle Load (W_f)</td>
                <td className="val-bold">
                  {trac.gross_vehicle_mass ? `${trac.gross_vehicle_mass.static_front_load_N.toFixed(1)} N` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>Static Rear Axle Load (W_r)</td>
                <td className="val-bold">
                  {trac.gross_vehicle_mass ? `${trac.gross_vehicle_mass.static_rear_load_N.toFixed(1)} N` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>Max FWD Tractive Force (F_max)</td>
                <td className="val-bold">
                  {trac.gross_vehicle_mass ? `${trac.gross_vehicle_mass.f_max_N.toFixed(1)} N` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>1st Gear Wheel Spin Check</td>
                <td>
                  {trac.gross_vehicle_mass ? (
                    <span className={`badge ${trac.gross_vehicle_mass.wheel_spin_1st_gear.spins ? 'badge-warning' : 'badge-success'}`}>
                      {trac.gross_vehicle_mass.wheel_spin_1st_gear.status}
                    </span>
                  ) : (
                    'N/A'
                  )}
                </td>
              </tr>
              <tr>
                <td>Road Resistance @ 100 km/h</td>
                <td className="val-bold">
                  {road.gross_vehicle_mass ? `${road.gross_vehicle_mass.power_at_100kmh.total_resistance_N.toFixed(1)} N` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>Engine Power Req. @ 100 km/h</td>
                <td className="val-bold">
                  {road.gross_vehicle_mass ? `${road.gross_vehicle_mass.power_at_100kmh.engine_power_kw.toFixed(2)} kW` : 'N/A'}
                </td>
              </tr>
              <tr>
                <td>Top-Speed Spare Force (Drawbar Pull)</td>
                <td>
                  {road.gross_vehicle_mass?.top_speed_check_6th_gear ? (
                    <span className="badge badge-success">
                      +{road.gross_vehicle_mass.top_speed_check_6th_gear.spare_force_drawbar_pull_N.toFixed(1)} N
                    </span>
                  ) : (
                    <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>
                      N/A (gear ratios unreleased)
                    </span>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Module Navigation Jump Cards */}
      <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-main)' }}>
        Explore Engineering Modules
      </h3>
      <div className="form-grid">
        <div className="card" style={{ marginBottom: 0, cursor: 'pointer' }} onClick={() => onNavigate('basic')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>Basic Calculations</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Tyre radii, CG distances & overall gear ratios</p>
            </div>
            <ArrowRight size={18} color="#2563eb" />
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0, cursor: 'pointer' }} onClick={() => onNavigate('drivetrain')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>Drivetrain & Speeds</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Tractive effort & speed across 1500, 2750 & 4000 rpm</p>
            </div>
            <ArrowRight size={18} color="#2563eb" />
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0, cursor: 'pointer' }} onClick={() => onNavigate('road_resistance')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>Road Resistance</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Aerodynamics, rolling resistance & 100 km/h power</p>
            </div>
            <ArrowRight size={18} color="#2563eb" />
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0, cursor: 'pointer' }} onClick={() => onNavigate('traction')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>Traction & Gradeability</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>FWD limit, wheel spin, grade angle & slip torque</p>
            </div>
            <ArrowRight size={18} color="#2563eb" />
          </div>
        </div>
      </div>
    </div>
  )
}
