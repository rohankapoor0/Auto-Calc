"""
Module B: Drivetrain Calculations (Formulas 7 - 10)
Implements tractive effort, vehicle speeds at engine speeds (1500, 2750, 4000 rpm),
and wheel torque demand according to the Creta Design Dossier.
"""

import math
from typing import Dict, List

from specifications import (
    GEAR_RATIOS,
    FINAL_DRIVE_RATIO,
    TRANSMISSION_EFFICIENCY,
    MAX_ENGINE_TORQUE,
    RATED_POWER_RPM,
    MAX_POWER_KW,
)
from basic_calculations import (
    calculate_overall_gear_ratio,
    calculate_torque_at_rated_power,
)


def calculate_tractive_effort(
    engine_torque: float,
    gear_ratio: float,
    dynamic_radius: float,
    final_drive_ratio: float = FINAL_DRIVE_RATIO,
    transmission_efficiency: float = TRANSMISSION_EFFICIENCY,
) -> float:
    """
    Formula 7: Tractive effort (page 5)
    F_TW = (T_e * i_g * i_f * eta_T) / r

    Args:
        engine_torque: Engine torque in Nm (T_e)
        gear_ratio: Transmission gear ratio (i_g)
        dynamic_radius: Dynamic rolling radius in m (r)
        final_drive_ratio: Final drive ratio (i_f)
        transmission_efficiency: Transmission efficiency (eta_T)

    Returns:
        Tractive effort F_TW in Newtons (N)
    """
    if dynamic_radius <= 0:
        raise ValueError("Dynamic rolling radius must be positive.")
    if transmission_efficiency <= 0:
        raise ValueError("Transmission efficiency must be positive.")

    overall_ratio = calculate_overall_gear_ratio(gear_ratio, final_drive_ratio)
    f_tw = (engine_torque * overall_ratio * transmission_efficiency) / dynamic_radius
    return f_tw


def calculate_vehicle_speed_mps(
    engine_rpm: float,
    gear_ratio: float,
    dynamic_radius: float,
    final_drive_ratio: float = FINAL_DRIVE_RATIO,
) -> float:
    """
    Formula 8: Vehicle speed in m/s (page 5)
    V = ((2 * pi * N / 60) * r) / (i_g * i_f)

    Args:
        engine_rpm: Engine rotational speed in rpm (N)
        gear_ratio: Transmission gear ratio (i_g)
        dynamic_radius: Dynamic rolling radius in m (r)
        final_drive_ratio: Final drive ratio (i_f)

    Returns:
        Vehicle speed V in metres per second (m/s)
    """
    if engine_rpm < 0:
        raise ValueError("Engine RPM cannot be negative.")
    if dynamic_radius <= 0:
        raise ValueError("Dynamic rolling radius must be positive.")
    overall_ratio = calculate_overall_gear_ratio(gear_ratio, final_drive_ratio)
    if overall_ratio == 0:
        raise ValueError("Overall gear ratio cannot be zero.")

    omega_engine = (2.0 * math.pi * engine_rpm) / 60.0
    v_mps = (omega_engine * dynamic_radius) / overall_ratio
    return v_mps


def convert_mps_to_kmh(speed_mps: float) -> float:
    """
    Formula 9: Vehicle speed conversion to km/h (page 5)
    V_kmh = 3.6 * V_mps

    Args:
        speed_mps: Speed in m/s

    Returns:
        Speed in km/h
    """
    return speed_mps * 3.6


def calculate_vehicle_speed_kmh(
    engine_rpm: float,
    gear_ratio: float,
    dynamic_radius: float,
    final_drive_ratio: float = FINAL_DRIVE_RATIO,
) -> float:
    """
    Convenience function combining Formula 8 and Formula 9.
    """
    v_mps = calculate_vehicle_speed_mps(
        engine_rpm, gear_ratio, dynamic_radius, final_drive_ratio
    )
    return convert_mps_to_kmh(v_mps)


def calculate_wheel_torque_demand(
    tractive_effort: float,
    dynamic_radius: float,
) -> float:
    """
    Formula 10: Wheel torque demand (page 7)
    T_demand = F_TW * r

    Args:
        tractive_effort: Tractive effort at the wheels F_TW in Newtons
        dynamic_radius: Dynamic rolling radius r in metres

    Returns:
        Wheel torque demand T_demand in Newton-metres (Nm)
    """
    if dynamic_radius <= 0:
        raise ValueError("Dynamic rolling radius must be positive.")
    return tractive_effort * dynamic_radius


def calculate_drivetrain_gear_table(
    dynamic_radius: float,
    max_engine_torque: float = MAX_ENGINE_TORQUE,
    max_power_kw: float = MAX_POWER_KW,
    rated_power_rpm: float = RATED_POWER_RPM,
    gear_ratios: Dict[int, float] = GEAR_RATIOS,
    final_drive_ratio: float = FINAL_DRIVE_RATIO,
    transmission_efficiency: float = TRANSMISSION_EFFICIENCY,
    rpm_checkpoints: List[float] = None,
) -> Dict[str, dict]:
    """
    Calculates tractive effort, wheel torque demand, and vehicle speeds across gears
    and rpm checkpoints (1500, 2750, 4000 rpm).
    Note: At 4000 rpm, Formula 5 rated-power torque is used instead of 250 Nm.
    """
    if rpm_checkpoints is None:
        rpm_checkpoints = [1500.0, 2750.0, 4000.0]

    t_rated = calculate_torque_at_rated_power(max_power_kw, rated_power_rpm)

    gear_results = {}
    for gear, i_g in gear_ratios.items():
        i_o = calculate_overall_gear_ratio(i_g, final_drive_ratio)

        # Torque plateau tractive effort (1500-2750 rpm, 250 Nm)
        f_tw_plateau = calculate_tractive_effort(
            max_engine_torque,
            i_g,
            dynamic_radius,
            final_drive_ratio,
            transmission_efficiency,
        )
        t_demand_plateau = calculate_wheel_torque_demand(f_tw_plateau, dynamic_radius)

        # 4000 rpm tractive effort (uses T_P from Formula 5)
        f_tw_rated = calculate_tractive_effort(
            t_rated,
            i_g,
            dynamic_radius,
            final_drive_ratio,
            transmission_efficiency,
        )
        t_demand_rated = calculate_wheel_torque_demand(f_tw_rated, dynamic_radius)

        speeds = {}
        for rpm in rpm_checkpoints:
            v_mps = calculate_vehicle_speed_mps(
                rpm, i_g, dynamic_radius, final_drive_ratio
            )
            v_kmh = convert_mps_to_kmh(v_mps)
            speeds[int(rpm)] = {
                "speed_mps": v_mps,
                "speed_kmh": v_kmh,
            }

        gear_results[gear] = {
            "gear": gear,
            "gear_ratio": i_g,
            "overall_ratio": i_o,
            "tractive_effort_plateau_N": f_tw_plateau,
            "wheel_torque_demand_plateau_Nm": t_demand_plateau,
            "tractive_effort_4000rpm_N": f_tw_rated,
            "wheel_torque_demand_4000rpm_Nm": t_demand_rated,
            "speeds_by_rpm": speeds,
        }

    return {
        "rated_power_torque_Nm": t_rated,
        "gears": gear_results,
    }
