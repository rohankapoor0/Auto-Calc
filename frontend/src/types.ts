/**
 * Types definition matching Python backend structures and specifications.
 */

export type FieldStatus = 'verified' | 'assumed' | 'unavailable' | 'SPECIFIED / GIVEN' | 'STANDARD CONSTANT'

export interface ProfileFieldItem<T = any> {
  value: T | null
  unit?: string
  status: FieldStatus
  rationale?: string
  note?: string
}

export interface VehicleProfile {
  id: string
  name: string
  variant: string
  model_year: string
  manufacturer: string
  fuel_type: string
  drivetrain: string
  transmission: string
  description: string
  source_reference: string
  source_url: string
  source_type: string

  dimensions: {
    length_mm: ProfileFieldItem<number>
    width_mm: ProfileFieldItem<number>
    height_mm: ProfileFieldItem<number>
    wheelbase_mm: ProfileFieldItem<number>
    ground_clearance_mm: ProfileFieldItem<number>
    boot_capacity_l: ProfileFieldItem<number>
    fuel_tank_capacity_l: ProfileFieldItem<number>
    turning_radius_m: ProfileFieldItem<number>
  }

  engine: {
    displacement_cc: ProfileFieldItem<number>
    cylinders: ProfileFieldItem<number>
    max_power_kw: ProfileFieldItem<number>
    rated_power_rpm: ProfileFieldItem<number>
    max_torque_nm: ProfileFieldItem<number>
    torque_rpm_range: ProfileFieldItem<string>
    torque_plateau_start_rpm: ProfileFieldItem<number>
    torque_plateau_end_rpm: ProfileFieldItem<number>
  }

  transmission_ratios: {
    gear_ratios: ProfileFieldItem<Record<number, number>>
    reverse_gear_ratio: ProfileFieldItem<number>
    final_drive_ratio: ProfileFieldItem<number>
    transmission_efficiency: ProfileFieldItem<number>
  }

  tyres: {
    tyre_spec: ProfileFieldItem<string>
    rim_diameter_in: ProfileFieldItem<number>
    width_mm: ProfileFieldItem<number>
    aspect_ratio: ProfileFieldItem<number>
    deflection_factor: ProfileFieldItem<number>
  }

  weights: {
    kerb_mass_kg: ProfileFieldItem<number>
    gross_vehicle_mass_kg: ProfileFieldItem<number>
    front_weight_share: ProfileFieldItem<number>
    cg_height_m: ProfileFieldItem<number>
  }

  aerodynamics_road: {
    drag_coefficient: ProfileFieldItem<number>
    frontal_area_m2: ProfileFieldItem<number>
    air_density_kg_m3: ProfileFieldItem<number>
    rolling_resistance_coeff: ProfileFieldItem<number>
    tyre_road_adhesion: ProfileFieldItem<number>
  }

  clutch: {
    outer_diameter_mm: ProfileFieldItem<number>
    inner_diameter_mm: ProfileFieldItem<number>
    friction_coefficient: ProfileFieldItem<number>
    friction_surfaces: ProfileFieldItem<number>
    safety_factor: ProfileFieldItem<number>
  }

  awd_hypothetical: {
    supported: boolean
    track_width_m?: ProfileFieldItem<number>
    test_speed_mps?: ProfileFieldItem<number>
    note?: string
  }
}

export interface SpecificationMetaItem {
  value: any
  unit: string
  status: FieldStatus
  rationale?: string
  note?: string
}

export type SpecificationMetadata = Record<string, SpecificationMetaItem>

export interface VehicleSpecifications {
  PROFILE_ID?: string
  VEHICLE_NAME?: string
  VARIANT?: string
  KERB_MASS: number | null
  GROSS_VEHICLE_MASS: number | null
  WHEELBASE: number | null
  CG_HEIGHT: number | null
  FRONT_WEIGHT_SHARE: number | null
  GRAVITY: number
  MAX_POWER_KW: number | null
  RATED_POWER_RPM: number | null
  MAX_ENGINE_TORQUE: number | null
  GEAR_RATIOS: Record<number, number> | null
  FINAL_DRIVE_RATIO: number | null
  TRANSMISSION_EFFICIENCY: number | null
  TYRE_RIM_DIAMETER_IN: number | null
  TYRE_WIDTH_MM: number | null
  TYRE_ASPECT_RATIO: number | null
  TYRE_DEFLECTION_FACTOR: number | null
  TYRE_ROAD_ADHESION: number | null
  AIR_DENSITY: number | null
  DRAG_COEFFICIENT: number | null
  FRONTAL_AREA: number | null
  ROLLING_RESISTANCE_COEFFICIENT: number | null
  CLUTCH_OUTER_DIAMETER_MM: number | null
  CLUTCH_INNER_DIAMETER_MM: number | null
  CLUTCH_FRICTION_COEFFICIENT: number | null
  CLUTCH_FRICTION_SURFACES: number | null
  CLUTCH_SAFETY_FACTOR: number | null
  MINIMUM_TURNING_RADIUS: number | null
  TRACK_WIDTH: number | null
  AWD_TEST_SPEED_MPS: number | null
  [key: string]: any
}

export interface BasicCalcResultItem {
  name: string
  value: number | Record<string, number> | null
  unit: string
  formula: string
  status?: string
  note?: string | null
}

export interface BasicCalculationsOutput {
  free_tyre_radius: BasicCalcResultItem
  dynamic_rolling_radius: BasicCalcResultItem
  kerb_weight: BasicCalcResultItem
  gross_vehicle_weight: BasicCalcResultItem
  torque_at_rated_power: BasicCalcResultItem
  cg_distance_front_L1: BasicCalcResultItem
  cg_distance_rear_L2: BasicCalcResultItem
  overall_gear_ratios: BasicCalcResultItem
}

export interface DrivetrainGearData {
  gear: number
  gear_ratio: number
  overall_ratio: number
  tractive_effort_plateau_N: number
  wheel_torque_demand_plateau_Nm: number
  tractive_effort_4000rpm_N: number
  wheel_torque_demand_4000rpm_Nm: number
  speeds_by_rpm: Record<number, { speed_mps: number; speed_kmh: number }>
}

export interface DrivetrainOutput {
  status: 'calculated' | 'incomplete'
  rated_power_torque_Nm: number | null
  gears: Record<string, DrivetrainGearData>
  formula_tractive_effort: string
  formula_vehicle_speed_mps: string
  formula_vehicle_speed_kmh: string
  formula_wheel_torque_demand: string
  note?: string
}

export interface RoadResistanceCase {
  weight_N: number
  power_at_100kmh: {
    speed_kmh: number
    speed_mps: number
    rolling_resistance_N: number
    aerodynamic_resistance_N: number
    grade_resistance_N: number
    total_resistance_N: number
    wheel_power_kw: number
    engine_power_kw: number
  }
  top_speed_check_6th_gear?: {
    rated_speed_mps: number
    rated_speed_kmh: number
    tractive_effort_N: number
    rolling_resistance_N: number
    aerodynamic_resistance_N: number
    grade_resistance_N: number
    total_resistance_N: number
    spare_force_drawbar_pull_N: number
    feasibility_status: string
    is_feasible: boolean
  } | null
  status?: string
}

export interface RoadResistanceOutput {
  air_resistance_constant: BasicCalcResultItem
  kerb_mass: RoadResistanceCase | null
  gross_vehicle_mass: RoadResistanceCase | null
}

export interface TractionCase {
  L1_m: number
  L2_m: number
  static_front_load_N: number
  static_rear_load_N: number
  f_max_N: number
  wheel_spin_1st_gear: {
    spins: boolean
    status: string
    excess_force_N: number
  }
  traction_factor_k: number
  gradeability: {
    gradeability_angle_rad: number
    gradeability_angle_deg: number
    gradient_percent: number
  }
  longitudinal_load_transfer_N: number
  dynamic_front_load_N: number
  tyre_slip_torque_Nm: number
  torque_demand_vs_slip: {
    exceeds_slip_torque: boolean
    wheel_torque_demand_Nm: number
    slip_torque_Nm: number
    excess_torque_Nm: number
    status: string
  }
}

export interface TractionOutput {
  status?: string
  kerb_mass: TractionCase | null
  gross_vehicle_mass: TractionCase | null
  formulas: Record<string, string>
}

export interface ClutchOutput {
  status?: string
  results: {
    outer_radius_r1_m: number
    inner_radius_r2_m: number
    mean_radius_R_m: number
    effective_radius_Reff_m: number
    design_torque_Tc_Nm: number
    axial_clamping_force_Wc_N: number
    torque_capacity_uniform_pressure_Nm: number
    average_contact_pressure_Pa: number
    average_contact_pressure_MPa: number
    uniform_wear_constant_C_Npm: number
    max_pressure_uniform_wear_Pa: number
    max_pressure_uniform_wear_MPa: number
    min_pressure_uniform_wear_Pa: number
    min_pressure_uniform_wear_MPa: number
  } | null
  formulas: Record<string, string>
  note?: string
}

export interface AWDCase {
  analysis_type: string
  inputs: Record<string, number>
  kinematics: {
    R_rear_m: number
    R_FI_m: number
    R_RO_m: number
    R_RI_m: number
    delta_outer_deg: number
    delta_inner_deg: number
    R_CG_m: number
    yaw_rate_rad_s: number
    wheel_speeds_rpm: Record<string, number>
  }
  dynamics: {
    lateral_acceleration_m_s2: number
    lateral_load_transfer_factor_lambda: number
    front_lateral_transfer_N: number
    rear_lateral_transfer_N: number
    wheel_vertical_loads_N: Record<string, number>
    remaining_mu_x: number
    wheel_max_longitudinal_forces_N: Record<string, number>
    wheel_max_torques_Nm: Record<string, number>
  }
  differential_comparison: {
    ideal_total_torque_capacity_Nm: number
    open_differential: { total_torque_Nm: number; percentage_of_ideal: number }
    fixed_60_40_center_differential: {
      total_torque_Nm: number
      percentage_of_ideal: number
      details: any
    }
    locked_center_differential: {
      total_torque_Nm: number
      percentage_of_ideal: number
      details: any
    }
    torque_vectoring_ideal: { total_torque_Nm: number; percentage_of_ideal: number }
  }
}

export interface AWDOutput {
  kerb_mass: AWDCase
  gross_vehicle_mass: AWDCase | null
}

export interface FullVehicleCalculationResponse {
  vehicle_specifications: SpecificationMetadata
  basic_calculations: BasicCalculationsOutput
  drivetrain: DrivetrainOutput
  road_resistance: RoadResistanceOutput
  traction: TractionOutput
  clutch: ClutchOutput
  awd_hypothetical?: AWDOutput
}
