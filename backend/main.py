"""
Interactive Command-Line Application for Hyundai Creta Engineering Calculations.
Provides formatted terminal inspection for all calculation modules, individual modules,
and optional hypothetical AWD calculations.
"""

import sys
from typing import Dict, Any

from calculator import run_full_vehicle_calculation
import specifications as spec


def print_header(title: str) -> None:
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


def print_subheader(title: str) -> None:
    print(f"\n--- {title} ---")


def display_specifications(data: Dict[str, Any]) -> None:
    print_header("1. TECHNICAL SPECIFICATIONS & PARAMETERS")
    print(f"{'Parameter':<32} {'Value':<18} {'Unit':<10} {'Origin'}")
    print("-" * 78)
    for name, meta in data["vehicle_specifications"].items():
        val = meta["value"]
        if isinstance(val, dict):
            val_str = "{" + ", ".join(f"G{k}:{v}" for k, v in val.items()) + "}"
        elif isinstance(val, float):
            val_str = f"{val:.4f}"
        else:
            val_str = str(val)
        print(f"{name:<32} {val_str:<18} {meta['unit']:<10} {meta['status']}")


def display_basic_calculations(data: Dict[str, Any]) -> None:
    print_header("2. BASIC VEHICLE CALCULATIONS (Formulas 1 - 6)")
    basic = data["basic_calculations"]
    for key, item in basic.items():
        if key == "overall_gear_ratios":
            print(f"\nOverall Gear Ratios (io = ig * if):")
            for gear, ratio in item["value"].items():
                print(f"  - Gear {gear}: {ratio:.4f}")
        else:
            print(f"- {item['name']:<40}: {item['value']:.5f} {item['unit']}")
            print(f"    Formula: {item['formula']}")


def display_drivetrain(data: Dict[str, Any]) -> None:
    print_header("3. DRIVETRAIN & PERFORMANCE (Formulas 7 - 10)")
    drive = data["drivetrain"]
    print(f"Rated Power Torque at 4000 rpm: {drive['rated_power_torque_Nm']:.2f} Nm (Formula 5)")
    print("\nGearbox Tractive Effort & Speeds across RPM Checkpoints:")
    print("-" * 78)
    print(f"{'Gear':<6} {'Ratio':<8} {'FTW @ 250Nm':<14} {'FTW @ 4000rpm':<15} {'1500 rpm':<11} {'2750 rpm':<11} {'4000 rpm'}")
    print(f"{'':<6} {'':<8} {'(N)':<14} {'(N)':<15} {'(km/h)':<11} {'(km/h)':<11} {'(km/h)'}")
    print("-" * 78)

    for g_num, g_data in drive["gears"].items():
        ftw_plat = g_data["tractive_effort_plateau_N"]
        ftw_rated = g_data["tractive_effort_4000rpm_N"]
        v1500 = g_data["speeds_by_rpm"][1500]["speed_kmh"]
        v2750 = g_data["speeds_by_rpm"][2750]["speed_kmh"]
        v4000 = g_data["speeds_by_rpm"][4000]["speed_kmh"]
        print(
            f"{g_num:<6} {g_data['gear_ratio']:<8.3f} {ftw_plat:<14.1f} {ftw_rated:<15.1f} "
            f"{v1500:<11.2f} {v2750:<11.2f} {v4000:.2f}"
        )


def display_road_resistance(data: Dict[str, Any]) -> None:
    print_header("4. ROAD RESISTANCE & POWER DEMAND (Formulas 11 - 21)")
    rr = data["road_resistance"]
    k_val = rr["air_resistance_constant"]["value"]
    print(f"Air Resistance Constant k = 0.5 * rho * Cd * A: {k_val:.4f} kg/m")

    for case_name, case_key in [("KERB MASS (1550 kg)", "kerb_mass"), ("GROSS VEHICLE MASS (1805 kg)", "gross_vehicle_mass")]:
        print_subheader(case_name)
        case_data = rr[case_key]
        p100 = case_data["power_at_100kmh"]
        top_check = case_data["top_speed_check_6th_gear"]

        print(f"Vehicle Weight: {case_data['weight_N']:.2f} N")
        print("\nPower Demand at 100 km/h (Level Road):")
        print(f"  - Rolling Resistance (R_RR)  : {p100['rolling_resistance_N']:.2f} N")
        print(f"  - Aerodynamic Drag (R_AF)    : {p100['aerodynamic_resistance_N']:.2f} N")
        print(f"  - Total Resistance (R_T)     : {p100['total_resistance_N']:.2f} N")
        print(f"  - Wheel Power Required       : {p100['wheel_power_kw']:.2f} kW")
        print(f"  - Engine Power Required      : {p100['engine_power_kw']:.2f} kW")

        print("\nTop-Speed Feasibility (6th Gear @ 4000 RPM Rated Power):")
        print(f"  - Speed at 4000 RPM          : {top_check['rated_speed_kmh']:.2f} km/h ({top_check['rated_speed_mps']:.2f} m/s)")
        print(f"  - Tractive Effort (F_TW)     : {top_check['tractive_effort_N']:.2f} N")
        print(f"  - Total Resistance (R_T)     : {top_check['total_resistance_N']:.2f} N")
        print(f"  - Drawbar Pull / Spare Force : {top_check['spare_force_drawbar_pull_N']:.2f} N")
        print(f"  - Status                     : {top_check['feasibility_status']}")


def display_traction(data: Dict[str, Any]) -> None:
    print_header("5. FWD TRACTION & GRADEABILITY (Formulas 22 - 32)")
    trac = data["traction"]

    for case_name, case_key in [("KERB MASS (1550 kg)", "kerb_mass"), ("GROSS VEHICLE MASS (1805 kg)", "gross_vehicle_mass")]:
        print_subheader(case_name)
        t_data = trac[case_key]

        print(f"Static Axle Distribution (L1 = {t_data['L1_m']:.3f} m, L2 = {t_data['L2_m']:.3f} m):")
        print(f"  - Front Axle Static Load (W_f) : {t_data['static_front_load_N']:.2f} N")
        print(f"  - Rear Axle Static Load (W_r)  : {t_data['static_rear_load_N']:.2f} N")

        print("\nTraction Limits & Wheel-Spin Check (1st Gear):")
        print(f"  - Max FWD Tractive Force (F_max)   : {t_data['f_max_N']:.2f} N")
        spin = t_data['wheel_spin_1st_gear']
        print(f"  - 1st Gear Spin Condition          : {spin['status']} (Excess: {spin['excess_force_N']:.2f} N)")

        print("\nGradeability:")
        g = t_data['gradeability']
        print(f"  - Traction Factor k                : {t_data['traction_factor_k']:.4f}")
        print(f"  - Maximum Grade Angle (theta)      : {g['gradeability_angle_deg']:.2f} deg ({g['gradeability_angle_rad']:.4f} rad)")
        print(f"  - Maximum Gradient (G)             : {g['gradient_percent']:.2f} %")

        print("\nDynamic Load Transfer & Torque Slip Check:")
        print(f"  - Longitudinal Load Transfer (Delta_W): {t_data['longitudinal_load_transfer_N']:.2f} N")
        print(f"  - Dynamic Front Axle Load (W_f,dyn): {t_data['dynamic_front_load_N']:.2f} N")
        print(f"  - Tyre Slip Torque (T_slip)        : {t_data['tyre_slip_torque_Nm']:.2f} Nm")
        comp = t_data['torque_demand_vs_slip']
        print(f"  - 1st Gear Wheel Torque Demand     : {comp['wheel_torque_demand_Nm']:.2f} Nm")
        print(f"  - Demand vs Slip Torque            : {comp['status']}")


def display_clutch(data: Dict[str, Any]) -> None:
    print_header("6. CLUTCH ANALYSIS (Formulas 33 - 43)")
    c = data["clutch"]["results"]
    print(f"Friction Radii: r1 = {c['outer_radius_r1_m']*1000:.1f} mm, r2 = {c['inner_radius_r2_m']*1000:.1f} mm")
    print(f"  - Mean Friction Radius (R)            : {c['mean_radius_R_m']:.4f} m ({c['mean_radius_R_m']*1000:.1f} mm)")
    print(f"  - Effective Radius (R_eff, unif. press): {c['effective_radius_Reff_m']:.4f} m ({c['effective_radius_Reff_m']*1000:.1f} mm)")
    print(f"  - Design Torque (T_c = SF * Te)       : {c['design_torque_Tc_Nm']:.2f} Nm")
    print(f"  - Axial Clamping Force (W_c)          : {c['axial_clamping_force_Wc_N']:.2f} N")
    print(f"  - Torque Capacity (Uniform Pressure)  : {c['torque_capacity_uniform_pressure_Nm']:.2f} Nm")
    print("\nContact Pressures:")
    print(f"  - Average Contact Pressure (p_avg)    : {c['average_contact_pressure_MPa']:.4f} MPa ({c['average_contact_pressure_Pa']:.1f} Pa)")
    print(f"  - Uniform Wear Constant (C)           : {c['uniform_wear_constant_C_Npm']:.2f} N/m")
    print(f"  - Max Pressure Uniform Wear (p_max)   : {c['max_pressure_uniform_wear_MPa']:.4f} MPa ({c['max_pressure_uniform_wear_Pa']:.1f} Pa)")
    print(f"  - Min Pressure Uniform Wear (p_min)   : {c['min_pressure_uniform_wear_MPa']:.4f} MPa ({c['min_pressure_uniform_wear_Pa']:.1f} Pa)")


def display_awd(data: Dict[str, Any]) -> None:
    if "awd_hypothetical" not in data:
        print("\nHypothetical AWD calculations not included.")
        return

    print_header("7. HYPOTHETICAL AWD EXTENSION (Formulas 44 - 70)")
    print("NOTE: This is an optional engineering study from pages 9-10 of the dossier.")

    for case_name, case_key in [("KERB MASS (1550 kg)", "kerb_mass"), ("GROSS VEHICLE MASS (1805 kg)", "gross_vehicle_mass")]:
        print_subheader(case_name)
        awd_data = data["awd_hypothetical"][case_key]
        kin = awd_data["kinematics"]
        dyn = awd_data["dynamics"]
        diff = awd_data["differential_comparison"]

        print("Cornering Kinematics (Ro = 5.3 m, Speed = 3.32 m/s):")
        print(f"  - Rear Axle Radius (R_r)       : {kin['R_rear_m']:.3f} m")
        print(f"  - CG Turning Radius (R_CG)     : {kin['R_CG_m']:.3f} m")
        print(f"  - Outer Steer Angle (delta_o)  : {kin['delta_outer_deg']:.2f} deg")
        print(f"  - Inner Steer Angle (delta_i)  : {kin['delta_inner_deg']:.2f} deg")
        print(f"  - Yaw Rate (Omega)             : {kin['yaw_rate_rad_s']:.4f} rad/s")
        print(f"  - Wheel Speeds (rpm)           : FO: {kin['wheel_speeds_rpm']['front_outer']:.1f}, "
              f"FI: {kin['wheel_speeds_rpm']['front_inner']:.1f}, "
              f"RO: {kin['wheel_speeds_rpm']['rear_outer']:.1f}, "
              f"RI: {kin['wheel_speeds_rpm']['rear_inner']:.1f}")

        print("\nCornering Dynamics & Load Transfer:")
        print(f"  - Lateral Accel (a_y)          : {dyn['lateral_acceleration_m_s2']:.3f} m/s^2")
        print(f"  - Transfer Factor (lambda)     : {dyn['lateral_load_transfer_factor_lambda']:.4f}")
        print(f"  - Remaining Friction (mu_x)    : {dyn['remaining_mu_x']:.4f}")

        w_loads = dyn["wheel_vertical_loads_N"]
        t_max = dyn["wheel_max_torques_Nm"]
        print(f"  - Wheel Vertical Loads (N)     : FO: {w_loads['F_z_FO']:.1f}, FI: {w_loads['F_z_FI']:.1f}, "
              f"RO: {w_loads['F_z_RO']:.1f}, RI: {w_loads['F_z_RI']:.1f}")
        print(f"  - Individual Max Torques (Nm)  : FO: {t_max['front_outer']:.1f}, FI: {t_max['front_inner']:.1f}, "
              f"RO: {t_max['rear_outer']:.1f}, RI: {t_max['rear_inner']:.1f}")

        print("\nDifferential Layout Comparison:")
        print(f"  - 1. Ideal Torque Vectoring    : {diff['torque_vectoring_ideal']['total_torque_Nm']:.1f} Nm (100.0 %)")
        print(f"  - 2. Open Differentials        : {diff['open_differential']['total_torque_Nm']:.1f} Nm "
              f"({diff['open_differential']['percentage_of_ideal']:.1f} % of ideal)")
        print(f"  - 3. Fixed 60:40 Centre Diff   : {diff['fixed_60_40_center_differential']['total_torque_Nm']:.1f} Nm "
              f"({diff['fixed_60_40_center_differential']['percentage_of_ideal']:.1f} % of ideal)")
        print(f"  - 4. Locked Centre Diff        : {diff['locked_center_differential']['total_torque_Nm']:.1f} Nm "
              f"({diff['locked_center_differential']['percentage_of_ideal']:.1f} % of ideal)")


def run_interactive_menu() -> None:
    print("\n" + "=" * 78)
    print(" HYUNDAI CRETA 1.5 U2 CRDi DIESEL - VEHICLE ENGINEERING CALCULATOR")
    print("=" * 78)
    print("Calculating results with default dossier specifications...")
    data = run_full_vehicle_calculation(include_awd=True)

    while True:
        print("\nAvailable Analyses:")
        print("  1. Run & Display Complete Vehicle Analysis (All Modules)")
        print("  2. View Vehicle Specifications & Defaults")
        print("  3. View Module A: Basic Vehicle Calculations (Tyre, Weight, Ratios, CG)")
        print("  4. View Module B: Drivetrain (Tractive Effort & Speed Tables)")
        print("  5. View Module C: Road Resistance & Power at 100 km/h (Kerb & GVW)")
        print("  6. View Module D: FWD Traction & Gradeability (Kerb & GVW)")
        print("  7. View Module E: Clutch Geometry, Clamping Force & Pressures")
        print("  8. View Module F: Hypothetical AWD Kinematics & Differentials")
        print("  q. Quit")

        choice = input("\nEnter choice [1-8 or q]: ").strip().lower()

        if choice == "1":
            display_specifications(data)
            display_basic_calculations(data)
            display_drivetrain(data)
            display_road_resistance(data)
            display_traction(data)
            display_clutch(data)
            display_awd(data)
        elif choice == "2":
            display_specifications(data)
        elif choice == "3":
            display_basic_calculations(data)
        elif choice == "4":
            display_drivetrain(data)
        elif choice == "5":
            display_road_resistance(data)
        elif choice == "6":
            display_traction(data)
        elif choice == "7":
            display_clutch(data)
        elif choice == "8":
            display_awd(data)
        elif choice in ("q", "quit", "exit"):
            print("Exiting calculator. Goodbye.")
            break
        else:
            print("Invalid selection. Please choose an option from 1 to 8 or q to quit.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        data = run_full_vehicle_calculation(include_awd=True)
        display_specifications(data)
        display_basic_calculations(data)
        display_drivetrain(data)
        display_road_resistance(data)
        display_traction(data)
        display_clutch(data)
        display_awd(data)
    else:
        run_interactive_menu()
