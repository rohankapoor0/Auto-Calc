"""
Central calculation engine module.
Coordinates all individual engineering calculation modules and aggregates
the results into structured dictionaries.
Supports graceful handling of unavailable parameters across diverse vehicle profiles.
"""

from typing import Dict, Any, Optional

import specifications as spec
import basic_calculations as basic
import drivetrain as drive
import road_resistance as road
import traction as trac
import clutch as clu
import awd


def run_full_vehicle_calculation(
    # Masses & Dimensions
    kerb_mass: Optional[float] = spec.KERB_MASS,
    gross_vehicle_mass: Optional[float] = spec.GROSS_VEHICLE_MASS,
    wheelbase: Optional[float] = spec.WHEELBASE,
    cg_height: Optional[float] = spec.CG_HEIGHT,
    front_weight_share: Optional[float] = spec.FRONT_WEIGHT_SHARE,
    gravity: float = spec.GRAVITY,
    # Powertrain
    max_power_kw: Optional[float] = spec.MAX_POWER_KW,
    rated_power_rpm: Optional[float] = spec.RATED_POWER_RPM,
    max_engine_torque: Optional[float] = spec.MAX_ENGINE_TORQUE,
    gear_ratios: Optional[Dict[int, float]] = None,
    final_drive_ratio: Optional[float] = spec.FINAL_DRIVE_RATIO,
    transmission_efficiency: Optional[float] = spec.TRANSMISSION_EFFICIENCY,
    # Tyres
    rim_diameter_in: Optional[float] = spec.TYRE_RIM_DIAMETER_IN,
    width_mm: Optional[float] = spec.TYRE_WIDTH_MM,
    aspect_ratio: Optional[float] = spec.TYRE_ASPECT_RATIO,
    deflection_factor: Optional[float] = spec.TYRE_DEFLECTION_FACTOR,
    tyre_road_adhesion: Optional[float] = spec.TYRE_ROAD_ADHESION,
    # Environment & Road
    air_density: Optional[float] = spec.AIR_DENSITY,
    drag_coefficient: Optional[float] = spec.DRAG_COEFFICIENT,
    frontal_area: Optional[float] = spec.FRONTAL_AREA,
    rolling_resistance_coeff: Optional[float] = spec.ROLLING_RESISTANCE_COEFFICIENT,
    # Clutch
    clutch_od_mm: Optional[float] = spec.CLUTCH_OUTER_DIAMETER_MM,
    clutch_id_mm: Optional[float] = spec.CLUTCH_INNER_DIAMETER_MM,
    clutch_friction_coeff: Optional[float] = spec.CLUTCH_FRICTION_COEFFICIENT,
    clutch_friction_surfaces: Optional[int] = spec.CLUTCH_FRICTION_SURFACES,
    clutch_safety_factor: Optional[float] = spec.CLUTCH_SAFETY_FACTOR,
    # AWD (Optional)
    include_awd: bool = False,
    awd_speed_mps: Optional[float] = spec.AWD_TEST_SPEED_MPS,
    turning_radius: Optional[float] = spec.MINIMUM_TURNING_RADIUS,
    track_width: Optional[float] = spec.TRACK_WIDTH,
    # Metadata passthrough
    spec_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes vehicle engineering calculations.
    For missing or unavailable parameters, marks corresponding sub-calculations
    as incomplete rather than inventing numbers.
    """
    if gear_ratios is None and spec.GEAR_RATIOS:
        # Only fallback if caller didn't pass gear_ratios at all
        gear_ratios = spec.GEAR_RATIOS.copy()

    # 1. Module A: Basic Calculations
    r_free = None
    r_dyn = None
    if rim_diameter_in and width_mm and aspect_ratio:
        r_free = basic.calculate_free_tyre_radius(rim_diameter_in, width_mm, aspect_ratio)
        if deflection_factor:
            r_dyn = basic.calculate_dynamic_rolling_radius(r_free, deflection_factor)

    w_kerb = basic.calculate_vehicle_weight(kerb_mass, gravity) if kerb_mass is not None else None
    w_gvw = basic.calculate_vehicle_weight(gross_vehicle_mass, gravity) if gross_vehicle_mass is not None else None

    overall_ratios = None
    if gear_ratios and final_drive_ratio:
        overall_ratios = basic.calculate_all_overall_gear_ratios(gear_ratios, final_drive_ratio)

    t_rated = None
    if max_power_kw and rated_power_rpm:
        t_rated = basic.calculate_torque_at_rated_power(max_power_kw, rated_power_rpm)

    l1, l2 = None, None
    if wheelbase and front_weight_share is not None:
        l1, l2 = basic.calculate_cg_reference_distances(wheelbase, front_weight_share)

    basic_results = {
        "free_tyre_radius": {
            "name": "Free Tyre Radius",
            "value": r_free,
            "unit": "m",
            "formula": "r_free = ((D_rim * 25.4 / 2) + (w * AR / 100)) / 1000",
            "status": "calculated" if r_free is not None else "unavailable",
        },
        "dynamic_rolling_radius": {
            "name": "Dynamic Rolling Radius",
            "value": r_dyn,
            "unit": "m",
            "formula": "r = f_d * r_free",
            "status": "calculated" if r_dyn is not None else "unavailable",
        },
        "kerb_weight": {
            "name": "Vehicle Weight (Kerb)",
            "value": w_kerb,
            "unit": "N",
            "formula": "W = M_kerb * g",
            "status": "calculated" if w_kerb is not None else "unavailable",
        },
        "gross_vehicle_weight": {
            "name": "Vehicle Weight (GVW)",
            "value": w_gvw,
            "unit": "N",
            "formula": "W = M_gvw * g",
            "status": "calculated" if w_gvw is not None else "unavailable",
        },
        "torque_at_rated_power": {
            "name": "Engine Torque at Rated Power",
            "value": t_rated,
            "unit": "Nm",
            "formula": "T_P = (P_max * 1000) / (2 * pi * N_P / 60)",
            "status": "calculated" if t_rated is not None else "unavailable",
        },
        "cg_distance_front_L1": {
            "name": "CG Distance from Front Axle (L1)",
            "value": l1,
            "unit": "m",
            "formula": "L1 = L - L2",
            "status": "calculated" if l1 is not None else "unavailable",
        },
        "cg_distance_rear_L2": {
            "name": "CG Distance from Rear Axle (L2)",
            "value": l2,
            "unit": "m",
            "formula": "L2 = s_f * L",
            "status": "calculated" if l2 is not None else "unavailable",
        },
        "overall_gear_ratios": {
            "name": "Overall Gear Ratios",
            "value": overall_ratios,
            "unit": "-",
            "formula": "i_o = i_g * i_f",
            "status": "calculated" if overall_ratios is not None else "unavailable",
            "note": "Gear ratios not published by manufacturer" if overall_ratios is None else None,
        },
    }

    # 2. Module B: Drivetrain Calculations
    drivetrain_results: Dict[str, Any] = {
        "status": "incomplete",
        "rated_power_torque_Nm": t_rated,
        "gears": {},
        "formula_tractive_effort": "F_TW = (T_e * i_g * i_f * eta_T) / r",
        "formula_vehicle_speed_mps": "V = ((2 * pi * N / 60) * r) / (i_g * i_f)",
        "formula_vehicle_speed_kmh": "V_kmh = 3.6 * V_mps",
        "formula_wheel_torque_demand": "T_demand = F_TW * r",
    }
    f_tw_1st = None

    if r_dyn and max_engine_torque and max_power_kw and rated_power_rpm and gear_ratios and final_drive_ratio and transmission_efficiency:
        drivetrain_data = drive.calculate_drivetrain_gear_table(
            dynamic_radius=r_dyn,
            max_engine_torque=max_engine_torque,
            max_power_kw=max_power_kw,
            rated_power_rpm=rated_power_rpm,
            gear_ratios=gear_ratios,
            final_drive_ratio=final_drive_ratio,
            transmission_efficiency=transmission_efficiency,
        )
        drivetrain_results["status"] = "calculated"
        drivetrain_results["gears"] = drivetrain_data["gears"]
        if 1 in drivetrain_data["gears"]:
            f_tw_1st = drivetrain_data["gears"][1]["tractive_effort_plateau_N"]
    else:
        drivetrain_results["note"] = (
            "Drivetrain speeds and tractive effort unavailable: requires verified gear ratios and final drive."
        )

    # 3. Module C: Road Resistance
    k_aero = None
    if air_density and drag_coefficient and frontal_area:
        k_aero = road.calculate_air_resistance_constant(air_density, drag_coefficient, frontal_area)

    road_resistance_results: Dict[str, Any] = {
        "air_resistance_constant": {
            "name": "Air Resistance Constant (k)",
            "value": k_aero,
            "unit": "kg/m",
            "formula": "k = 0.5 * rho * C_D * A",
            "status": "calculated" if k_aero is not None else "unavailable",
        },
        "kerb_mass": None,
        "gross_vehicle_mass": None,
    }

    if k_aero and rolling_resistance_coeff and transmission_efficiency:
        # Check Kerb case
        if w_kerb is not None:
            p100_kerb = road.calculate_power_at_100kmh(
                w_kerb, air_density, drag_coefficient, frontal_area,
                rolling_resistance_coeff, transmission_efficiency
            )
            top_check_kerb = None
            if gear_ratios and final_drive_ratio and r_dyn and max_power_kw and rated_power_rpm:
                top_gear = max(gear_ratios.keys())
                top_check_kerb = road.evaluate_top_speed_feasibility(
                    gear_ratios[top_gear], r_dyn, w_kerb, final_drive_ratio, transmission_efficiency,
                    max_power_kw, rated_power_rpm, air_density, drag_coefficient, frontal_area,
                    rolling_resistance_coeff
                )
            road_resistance_results["kerb_mass"] = {
                "weight_N": w_kerb,
                "power_at_100kmh": p100_kerb,
                "top_speed_check_6th_gear": top_check_kerb,
                "status": "calculated",
            }

        # Check GVW case
        if w_gvw is not None:
            p100_gvw = road.calculate_power_at_100kmh(
                w_gvw, air_density, drag_coefficient, frontal_area,
                rolling_resistance_coeff, transmission_efficiency
            )
            top_check_gvw = None
            if gear_ratios and final_drive_ratio and r_dyn and max_power_kw and rated_power_rpm:
                top_gear = max(gear_ratios.keys())
                top_check_gvw = road.evaluate_top_speed_feasibility(
                    gear_ratios[top_gear], r_dyn, w_gvw, final_drive_ratio, transmission_efficiency,
                    max_power_kw, rated_power_rpm, air_density, drag_coefficient, frontal_area,
                    rolling_resistance_coeff
                )
            road_resistance_results["gross_vehicle_mass"] = {
                "weight_N": w_gvw,
                "power_at_100kmh": p100_gvw,
                "top_speed_check_6th_gear": top_check_gvw,
                "status": "calculated",
            }

    # 4. Module D: Traction and Gradeability
    traction_results: Dict[str, Any] = {
        "status": "incomplete",
        "kerb_mass": None,
        "gross_vehicle_mass": None,
        "formulas": {
            "static_front_load": "W_f = (W * L_2) / L",
            "static_rear_load": "W_r = (W * L_1) / L",
            "max_tractive_force_fwd": "F_max = (mu * W * L_2) / (L + mu * h)",
            "wheel_spin": "F_TW > F_max",
            "traction_factor": "k = F_max / W",
            "gradeability_angle": "theta = sin^-1(k / sqrt(1 + fr^2)) - tan^-1(fr)",
            "gradient_percentage": "G = 100 * tan(theta)",
            "longitudinal_transfer": "Delta_W = (F_max * h) / L",
            "dynamic_front_load": "W_f_dyn = W_f - Delta_W",
            "tyre_slip_torque": "T_slip = eta * mu * W_f_dyn * r",
        },
    }

    # Can compute static loads & F_max whenever weight, wheelbase, cg_height, and mu are present
    if wheelbase and cg_height and tyre_road_adhesion and rolling_resistance_coeff and r_dyn:
        # Fallback for f_tw_1st if gear ratio is unavailable: pass 0.0 so wheel spin reports 'unavailable'
        has_1st_gear_force = f_tw_1st is not None

        if w_kerb is not None:
            eff_1st = f_tw_1st if has_1st_gear_force else 0.0
            t_kerb = trac.perform_complete_traction_analysis(
                w_kerb, r_dyn, eff_1st, wheelbase, cg_height, tyre_road_adhesion,
                rolling_resistance_coeff, front_weight_share
            )
            if not has_1st_gear_force:
                t_kerb["wheel_spin_1st_gear"]["status"] = "Unavailable (requires verified 1st gear ratio)"
                t_kerb["torque_demand_vs_slip"]["status"] = "Unavailable (requires verified 1st gear ratio)"
            traction_results["kerb_mass"] = t_kerb

        if w_gvw is not None:
            eff_1st = f_tw_1st if has_1st_gear_force else 0.0
            t_gvw = trac.perform_complete_traction_analysis(
                w_gvw, r_dyn, eff_1st, wheelbase, cg_height, tyre_road_adhesion,
                rolling_resistance_coeff, front_weight_share
            )
            if not has_1st_gear_force:
                t_gvw["wheel_spin_1st_gear"]["status"] = "Unavailable (requires verified 1st gear ratio)"
                t_gvw["torque_demand_vs_slip"]["status"] = "Unavailable (requires verified 1st gear ratio)"
            traction_results["gross_vehicle_mass"] = t_gvw

        traction_results["status"] = "calculated"

    # 5. Module E: Clutch Analysis
    clutch_results: Dict[str, Any] = {
        "status": "incomplete",
        "results": None,
        "formulas": {
            "outer_radius": "r_1 = OD / 2 (m)",
            "inner_radius": "r_2 = ID / 2 (m)",
            "mean_radius": "R = (r_1 + r_2) / 2",
            "design_torque": "T_c = SF * T_e",
            "axial_clamping_force": "W_c = T_c / (n * mu_c * R)",
            "effective_radius": "R_eff = (2/3) * (r_1^3 - r_2^3) / (r_1^2 - r_2^2)",
            "torque_capacity_uniform_pressure": "T = n * mu_c * W_c * R_eff",
            "average_contact_pressure": "p_avg = W_c / (pi * (r_1^2 - r_2^2))",
            "uniform_wear_constant": "C = W_c / (2 * pi * (r_1 - r_2))",
            "max_pressure_uniform_wear": "p_max = C / r_2",
            "min_pressure_uniform_wear": "p_min = C / r_1",
        },
    }

    if clutch_od_mm and clutch_id_mm and max_engine_torque and clutch_safety_factor and clutch_friction_coeff and clutch_friction_surfaces:
        clutch_data = clu.perform_complete_clutch_analysis(
            clutch_od_mm, clutch_id_mm, max_engine_torque,
            clutch_safety_factor, clutch_friction_coeff, clutch_friction_surfaces
        )
        clutch_results["results"] = clutch_data
        clutch_results["status"] = "calculated"
    else:
        clutch_results["note"] = (
            "Clutch contact pressure calculations unavailable: clutch dimensions (OD/ID) are proprietary service data not published by manufacturer."
        )

    # Output structure
    output = {
        "vehicle_specifications": spec_metadata if spec_metadata else spec.SPECIFICATION_METADATA,
        "basic_calculations": basic_results,
        "drivetrain": drivetrain_results,
        "road_resistance": road_resistance_results,
        "traction": traction_results,
        "clutch": clutch_results,
    }

    # Optional AWD extension
    if include_awd and track_width and turning_radius and r_dyn and wheelbase and front_weight_share and cg_height and tyre_road_adhesion:
        awd_kerb = awd.perform_complete_awd_analysis(
            dynamic_radius=r_dyn,
            mass_kg=kerb_mass if kerb_mass is not None else 1550.0,
            speed_mps=awd_speed_mps if awd_speed_mps else 3.32,
            outer_turning_radius=turning_radius,
            track_width=track_width,
            wheelbase=wheelbase,
            front_weight_share=front_weight_share,
            cg_height=cg_height,
            mu=tyre_road_adhesion,
            g=gravity,
        )
        awd_gvw = None
        if gross_vehicle_mass is not None:
            awd_gvw = awd.perform_complete_awd_analysis(
                dynamic_radius=r_dyn,
                mass_kg=gross_vehicle_mass,
                speed_mps=awd_speed_mps if awd_speed_mps else 3.32,
                outer_turning_radius=turning_radius,
                track_width=track_width,
                wheelbase=wheelbase,
                front_weight_share=front_weight_share,
                cg_height=cg_height,
                mu=tyre_road_adhesion,
                g=gravity,
            )
        output["awd_hypothetical"] = {
            "kerb_mass": awd_kerb,
            "gross_vehicle_mass": awd_gvw,
        }

    return output
