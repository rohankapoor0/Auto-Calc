"""
Module A: Basic Calculations (Formulas 1 - 6)
Implements tyre geometry, vehicle weight, overall gear ratios, rated-power engine torque,
and center-of-gravity (CG) reference distances according to the Creta Design Dossier.
"""

import math
from typing import Dict, Tuple

from specifications import (
    TYRE_RIM_DIAMETER_IN,
    TYRE_WIDTH_MM,
    TYRE_ASPECT_RATIO,
    TYRE_DEFLECTION_FACTOR,
    GRAVITY,
    FINAL_DRIVE_RATIO,
    GEAR_RATIOS,
    MAX_POWER_KW,
    RATED_POWER_RPM,
    WHEELBASE,
    FRONT_WEIGHT_SHARE,
)


def calculate_free_tyre_radius(
    rim_diameter_in: float = TYRE_RIM_DIAMETER_IN,
    width_mm: float = TYRE_WIDTH_MM,
    aspect_ratio: float = TYRE_ASPECT_RATIO,
) -> float:
    """
    Formula 1: Free tyre radius (page 4)
    r_free = ((D_rim * 25.4 / 2) + (w * AR / 100)) / 1000

    Args:
        rim_diameter_in: Rim diameter in inches (D_rim)
        width_mm: Tyre width in mm (w)
        aspect_ratio: Tyre aspect ratio in percent (AR)

    Returns:
        r_free in metres (m)
    """
    if rim_diameter_in <= 0 or width_mm <= 0 or aspect_ratio <= 0:
        raise ValueError("Tyre dimensions must be positive values.")
    rim_radius_mm = (rim_diameter_in * 25.4) / 2.0
    sidewall_height_mm = width_mm * (aspect_ratio / 100.0)
    r_free_m = (rim_radius_mm + sidewall_height_mm) / 1000.0
    return r_free_m


def calculate_dynamic_rolling_radius(
    r_free: float,
    deflection_factor: float = TYRE_DEFLECTION_FACTOR,
) -> float:
    """
    Formula 2: Dynamic rolling radius (page 4)
    r = f_d * r_free

    Args:
        r_free: Free tyre radius in metres
        deflection_factor: Tyre deflection factor f_d (default: 0.97)

    Returns:
        Dynamic rolling radius r in metres (m)
    """
    if r_free <= 0:
        raise ValueError("Free tyre radius must be positive.")
    if deflection_factor <= 0 or deflection_factor > 1.0:
        raise ValueError("Deflection factor must be in the range (0, 1.0].")
    return deflection_factor * r_free


def calculate_vehicle_weight(
    mass_kg: float,
    g: float = GRAVITY,
) -> float:
    """
    Formula 3: Vehicle weight (page 4)
    W = M * g

    Args:
        mass_kg: Mass in kilograms (kerb mass or gross vehicle mass)
        g: Acceleration due to gravity in m/s^2

    Returns:
        Weight W in Newtons (N)
    """
    if mass_kg < 0:
        raise ValueError("Mass cannot be negative.")
    if g <= 0:
        raise ValueError("Gravity must be positive.")
    return mass_kg * g


def calculate_overall_gear_ratio(
    gear_ratio: float,
    final_drive_ratio: float = FINAL_DRIVE_RATIO,
) -> float:
    """
    Formula 4: Overall gear ratio (page 4)
    i_o = i_g * i_f

    Args:
        gear_ratio: Gear ratio for specific forward gear (i_g)
        final_drive_ratio: Final drive ratio (i_f)

    Returns:
        Overall ratio i_o
    """
    if gear_ratio == 0 or final_drive_ratio == 0:
        raise ValueError("Gear ratios cannot be zero.")
    return gear_ratio * final_drive_ratio


def calculate_all_overall_gear_ratios(
    gear_ratios: Dict[int, float] = GEAR_RATIOS,
    final_drive_ratio: float = FINAL_DRIVE_RATIO,
) -> Dict[int, float]:
    """
    Calculates overall gear ratio for all provided forward gears.
    """
    return {
        gear: calculate_overall_gear_ratio(ratio, final_drive_ratio)
        for gear, ratio in gear_ratios.items()
    }


def calculate_torque_at_rated_power(
    power_kw: float = MAX_POWER_KW,
    rated_rpm: float = RATED_POWER_RPM,
) -> float:
    """
    Formula 5: Torque at rated power (page 4)
    T_P = (P_max * 1000) / (2 * pi * N_P / 60)

    Args:
        power_kw: Maximum rated power in kW (P_max)
        rated_rpm: Engine speed at rated power in rpm (N_P)

    Returns:
        Engine torque at rated power T_P in Newton-metres (Nm)
    """
    if power_kw <= 0:
        raise ValueError("Power must be positive.")
    if rated_rpm <= 0:
        raise ValueError("Rated RPM must be positive and non-zero.")
    omega = (2.0 * math.pi * rated_rpm) / 60.0
    return (power_kw * 1000.0) / omega


def calculate_cg_reference_distances(
    wheelbase: float = WHEELBASE,
    front_weight_share: float = FRONT_WEIGHT_SHARE,
) -> Tuple[float, float]:
    """
    Formula 6: CG reference distances (page 4)
    L_2 = s_f * L
    L_1 = L - L_2

    Where:
    - L_2 is the longitudinal distance from the rear axle to the CG
    - L_1 is the longitudinal distance from the front axle to the CG
    - s_f is front weight share (0.61)
    - L is wheelbase

    Args:
        wheelbase: Wheelbase L in metres
        front_weight_share: Front weight share s_f (0.0 to 1.0)

    Returns:
        Tuple (L_1, L_2) in metres
    """
    if wheelbase <= 0:
        raise ValueError("Wheelbase must be positive.")
    if not (0.0 <= front_weight_share <= 1.0):
        raise ValueError("Front weight share must be between 0.0 and 1.0.")
    l2 = front_weight_share * wheelbase
    l1 = wheelbase - l2
    return l1, l2
