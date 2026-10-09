"""
Module C: Road Resistance and Vehicle Performance (Formulas 11 - 21)
Implements aerodynamic resistance, rolling resistance, grade resistance,
total resistance, drawbar pull, power requirements, and top-speed feasibility
according to the Creta Design Dossier.
"""

import math
from typing import Dict, Tuple

from specifications import (
    AIR_DENSITY,
    DRAG_COEFFICIENT,
    FRONTAL_AREA,
    ROLLING_RESISTANCE_COEFFICIENT,
    TRANSMISSION_EFFICIENCY,
    RATED_POWER_RPM,
    MAX_POWER_KW,
    FINAL_DRIVE_RATIO,
    GEAR_RATIOS,
)
from basic_calculations import (
    calculate_overall_gear_ratio,
    calculate_torque_at_rated_power,
)
from drivetrain import (
    calculate_tractive_effort,
    calculate_vehicle_speed_mps,
    convert_mps_to_kmh,
)


def calculate_air_resistance_constant(
    air_density: float = AIR_DENSITY,
    drag_coefficient: float = DRAG_COEFFICIENT,
    frontal_area: float = FRONTAL_AREA,
) -> float:
    """
    Formula 11: Air resistance constant (page 6)
    k = 0.5 * rho * C_D * A

    Args:
        air_density: Air density rho in kg/m^3
        drag_coefficient: Aerodynamic drag coefficient C_D
        frontal_area: Frontal area A in m^2

    Returns:
        Air resistance constant k in kg/m
    """
    if air_density <= 0 or drag_coefficient <= 0 or frontal_area <= 0:
        raise ValueError("Air density, drag coefficient, and frontal area must be positive.")
    return 0.5 * air_density * drag_coefficient * frontal_area


def calculate_rolling_resistance(
    weight: float,
    rolling_resistance_coeff: float = ROLLING_RESISTANCE_COEFFICIENT,
) -> float:
    """
    Formula 12: Rolling resistance (page 6)
    R_RR = f_r * W

    Args:
        weight: Vehicle weight W in Newtons
        rolling_resistance_coeff: Rolling resistance coefficient f_r

    Returns:
        Rolling resistance R_RR in Newtons (N)
    """
    if weight < 0 or rolling_resistance_coeff < 0:
        raise ValueError("Weight and rolling resistance coefficient cannot be negative.")
    return rolling_resistance_coeff * weight


def calculate_aerodynamic_resistance(
    speed_mps: float,
    air_density: float = AIR_DENSITY,
    drag_coefficient: float = DRAG_COEFFICIENT,
    frontal_area: float = FRONTAL_AREA,
) -> float:
    """
    Formula 13: Aerodynamic resistance (page 6)
    R_AF = 0.5 * rho * C_D * A * V^2 = k * V^2

    Implemented once by reusing Formula 11 (calculate_air_resistance_constant).

    Args:
        speed_mps: Vehicle speed V in m/s
        air_density: rho (kg/m^3)
        drag_coefficient: C_D
        frontal_area: A (m^2)

    Returns:
        Aerodynamic resistance R_AF in Newtons (N)
    """
    if speed_mps < 0:
        raise ValueError("Speed cannot be negative.")
    k = calculate_air_resistance_constant(air_density, drag_coefficient, frontal_area)
    return k * (speed_mps ** 2)


def calculate_grade_resistance(
    weight: float,
    grade_angle_rad: float = 0.0,
) -> float:
    """
    Formula 14: Grade resistance (page 6)
    R_GR = W * sin(theta)
    For level road: theta = 0, R_GR = 0

    Args:
        weight: Vehicle weight W in Newtons
        grade_angle_rad: Grade angle theta in radians

    Returns:
        Grade resistance R_GR in Newtons (N)
    """
    if weight < 0:
        raise ValueError("Weight cannot be negative.")
    return weight * math.sin(grade_angle_rad)


def calculate_total_road_resistance(
    rolling_resistance: float,
    aerodynamic_resistance: float,
    grade_resistance: float = 0.0,
) -> float:
    """
    Formula 15: Total road resistance (page 6)
    R_T = R_RR + R_AF + R_GR

    Args:
        rolling_resistance: R_RR in N
        aerodynamic_resistance: R_AF in N
        grade_resistance: R_GR in N (default 0.0)

    Returns:
        Total road resistance R_T in Newtons (N)
    """
    return rolling_resistance + aerodynamic_resistance + grade_resistance


def calculate_drawbar_pull(
    tractive_effort: float,
    total_resistance: float,
) -> float:
    """
    Formula 16: Drawbar pull (page 6)
    F_db = F_TW - R_T

    Args:
        tractive_effort: Available tractive effort F_TW in N
        total_resistance: Total opposing road resistance R_T in N

    Returns:
        Drawbar pull F_db in Newtons (N)
    """
    return tractive_effort - total_resistance


def calculate_wheel_power_kw(
    total_resistance: float,
    speed_mps: float,
) -> float:
    """
    Formula 17: Wheel power (page 6)
    P_wheel = R_T * V  (Watts)
    P_wheel_kW = (R_T * V) / 1000

    Args:
        total_resistance: Total resistance R_T in N
        speed_mps: Vehicle speed V in m/s

    Returns:
        Wheel power in kilowatts (kW)
    """
    if speed_mps < 0:
        raise ValueError("Speed cannot be negative.")
    power_watts = total_resistance * speed_mps
    return power_watts / 1000.0


def calculate_engine_power_required_kw(
    wheel_power_kw: float,
    transmission_efficiency: float = TRANSMISSION_EFFICIENCY,
) -> float:
    """
    Formula 18: Engine power required (page 6)
    P_engine = P_wheel / eta_T

    Args:
        wheel_power_kw: Wheel power in kW
        transmission_efficiency: Mechanical transmission efficiency eta_T

    Returns:
        Engine power required in kilowatts (kW)
    """
    if transmission_efficiency <= 0:
        raise ValueError("Transmission efficiency must be positive.")
    return wheel_power_kw / transmission_efficiency


def calculate_engine_speed_from_road_speed(
    speed_mps: float,
    dynamic_radius: float,
    overall_ratio: float,
) -> float:
    """
    Formula 19: Engine speed at a given road speed (page 6)
    N_engine = (V / r) * (60 / (2 * pi)) * i_o

    Args:
        speed_mps: Vehicle speed V in m/s
        dynamic_radius: Dynamic rolling radius r in m
        overall_ratio: Overall gear ratio i_o

    Returns:
        Engine speed N_engine in rpm
    """
    if speed_mps < 0:
        raise ValueError("Speed cannot be negative.")
    if dynamic_radius <= 0:
        raise ValueError("Dynamic rolling radius must be positive.")
    if overall_ratio == 0:
        raise ValueError("Overall gear ratio cannot be zero.")

    omega_wheel = speed_mps / dynamic_radius
    n_engine = omega_wheel * (60.0 / (2.0 * math.pi)) * overall_ratio
    return n_engine


def evaluate_top_speed_feasibility(
    gear_ratio: float,
    dynamic_radius: float,
    weight: float,
    final_drive_ratio: float = FINAL_DRIVE_RATIO,
    transmission_efficiency: float = TRANSMISSION_EFFICIENCY,
    max_power_kw: float = MAX_POWER_KW,
    rated_power_rpm: float = RATED_POWER_RPM,
    air_density: float = AIR_DENSITY,
    drag_coefficient: float = DRAG_COEFFICIENT,
    frontal_area: float = FRONTAL_AREA,
    rolling_resistance_coeff: float = ROLLING_RESISTANCE_COEFFICIENT,
    grade_angle_rad: float = 0.0,
) -> Dict[str, float | str | bool]:
    """
    Formula 20: Top-speed feasibility check (page 6)
    Uses Formula 5 for T_P, calculates vehicle speed at rated rpm (Formula 8),
    evaluates road resistance at that speed, tractive effort F_TW, and drawbar pull F_db = F_TW - R_T.
    Reports whether spare force is positive, zero, or negative.
    Treat this as the dossier's theoretical top-speed check, not a real-world guarantee.
    """
    # 1. Torque at rated power (Formula 5)
    t_p = calculate_torque_at_rated_power(max_power_kw, rated_power_rpm)

    # 2. Vehicle speed at rated power rpm in specified gear (Formula 8)
    speed_mps = calculate_vehicle_speed_mps(
        rated_power_rpm, gear_ratio, dynamic_radius, final_drive_ratio
    )
    speed_kmh = convert_mps_to_kmh(speed_mps)

    # 3. Available tractive effort at rated power rpm
    f_tw = calculate_tractive_effort(
        t_p, gear_ratio, dynamic_radius, final_drive_ratio, transmission_efficiency
    )

    # 4. Total road resistance at this speed (Formulas 12-15)
    r_rr = calculate_rolling_resistance(weight, rolling_resistance_coeff)
    r_af = calculate_aerodynamic_resistance(speed_mps, air_density, drag_coefficient, frontal_area)
    r_gr = calculate_grade_resistance(weight, grade_angle_rad)
    r_t = calculate_total_road_resistance(r_rr, r_af, r_gr)

    # 5. Drawbar pull (Formula 16)
    f_db = calculate_drawbar_pull(f_tw, r_t)

    # Status assessment
    if abs(f_db) < 1e-3:
        feasibility_status = "ZERO (Exact Equilibrium)"
        feasible = True
    elif f_db > 0:
        feasibility_status = "POSITIVE (Excess Tractive Force Available)"
        feasible = True
    else:
        feasibility_status = "NEGATIVE (Force Deficit / Feasibility Limited)"
        feasible = False

    return {
        "rated_speed_mps": speed_mps,
        "rated_speed_kmh": speed_kmh,
        "tractive_effort_N": f_tw,
        "rolling_resistance_N": r_rr,
        "aerodynamic_resistance_N": r_af,
        "grade_resistance_N": r_gr,
        "total_resistance_N": r_t,
        "spare_force_drawbar_pull_N": f_db,
        "feasibility_status": feasibility_status,
        "is_feasible": feasible,
    }


def calculate_power_at_100kmh(
    weight: float,
    air_density: float = AIR_DENSITY,
    drag_coefficient: float = DRAG_COEFFICIENT,
    frontal_area: float = FRONTAL_AREA,
    rolling_resistance_coeff: float = ROLLING_RESISTANCE_COEFFICIENT,
    transmission_efficiency: float = TRANSMISSION_EFFICIENCY,
    grade_angle_rad: float = 0.0,
) -> Dict[str, float]:
    """
    Formula 21: Power requirement at 100 km/h (page 6)
    V = 100 / 3.6 m/s
    Reuses formulas 12-18 to calculate total resistance, wheel power, and engine power.

    Args:
        weight: Vehicle weight W in Newtons (kerb mass or GVW)

    Returns:
        Dict with resistance components, wheel power (kW), and engine power (kW).
    """
    v_mps = 100.0 / 3.6  # 27.7778 m/s
    r_rr = calculate_rolling_resistance(weight, rolling_resistance_coeff)
    r_af = calculate_aerodynamic_resistance(v_mps, air_density, drag_coefficient, frontal_area)
    r_gr = calculate_grade_resistance(weight, grade_angle_rad)
    r_t = calculate_total_road_resistance(r_rr, r_af, r_gr)

    p_wheel_kw = calculate_wheel_power_kw(r_t, v_mps)
    p_engine_kw = calculate_engine_power_required_kw(p_wheel_kw, transmission_efficiency)

    return {
        "speed_kmh": 100.0,
        "speed_mps": v_mps,
        "rolling_resistance_N": r_rr,
        "aerodynamic_resistance_N": r_af,
        "grade_resistance_N": r_gr,
        "total_resistance_N": r_t,
        "wheel_power_kw": p_wheel_kw,
        "engine_power_kw": p_engine_kw,
    }
