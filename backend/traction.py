"""
Module D: FWD Traction and Gradeability Calculations (Formulas 22 - 32)
Implements static axle loads, maximum tractive force for FWD, wheel-spin condition,
traction factor, gradeability angle and gradient percentage, longitudinal load transfer,
dynamic axle loads, and tyre slip torque according to the Creta Design Dossier.
"""

import math
from typing import Dict

from specifications import (
    WHEELBASE,
    CG_HEIGHT,
    TYRE_ROAD_ADHESION,
    ROLLING_RESISTANCE_COEFFICIENT,
)
from basic_calculations import calculate_cg_reference_distances
from drivetrain import calculate_wheel_torque_demand


def calculate_static_axle_loads(
    weight: float,
    wheelbase: float = WHEELBASE,
    front_weight_share: float = None,
    l1: float = None,
    l2: float = None,
) -> Dict[str, float]:
    """
    Formula 22 & 23: Static axle loads (page 7)
    W_f = (W * L_2) / L
    W_r = (W * L_1) / L

    Args:
        weight: Vehicle weight W in N
        wheelbase: Wheelbase L in m
        front_weight_share: Optional sf
        l1: Optional distance from front axle to CG in m
        l2: Optional distance from rear axle to CG in m

    Returns:
        Dict with 'W_f' (front axle load in N) and 'W_r' (rear axle load in N)
    """
    if wheelbase <= 0:
        raise ValueError("Wheelbase must be positive.")
    if l1 is None or l2 is None:
        if front_weight_share is not None:
            l1, l2 = calculate_cg_reference_distances(wheelbase, front_weight_share)
        else:
            l1, l2 = calculate_cg_reference_distances(wheelbase)

    w_f = (weight * l2) / wheelbase
    w_r = (weight * l1) / wheelbase
    return {"W_f": w_f, "W_r": w_r}


def calculate_max_tractive_force_fwd(
    weight: float,
    l2: float,
    wheelbase: float = WHEELBASE,
    cg_height: float = CG_HEIGHT,
    mu: float = TYRE_ROAD_ADHESION,
) -> float:
    """
    Formula 24: Maximum tractive force for FWD (page 7)
    F_max = (mu * W * L_2) / (L + mu * h)

    Args:
        weight: Total vehicle weight W in N
        l2: Distance from rear axle to CG in m
        wheelbase: Wheelbase L in m
        cg_height: Centre of gravity height h in m
        mu: Tyre-road adhesion coefficient mu

    Returns:
        Maximum tractive force F_max in Newtons (N)
    """
    denom = wheelbase + (mu * cg_height)
    if denom <= 0:
        raise ValueError("Denominator (L + mu * h) must be positive.")
    f_max = (mu * weight * l2) / denom
    return f_max


def check_wheel_spin(
    tractive_effort: float,
    f_max: float,
) -> Dict[str, bool | str | float]:
    """
    Formula 25: Wheel-spin condition (page 7)
    F_TW > F_max

    Args:
        tractive_effort: Actual tractive effort at wheels F_TW in N
        f_max: Maximum tractive force before slip in N

    Returns:
        Dict with boolean 'spins', condition string, and margin.
    """
    spins = tractive_effort > f_max
    margin = tractive_effort - f_max
    return {
        "spins": spins,
        "status": "WHEEL SPIN OCCURS" if spins else "NO WHEEL SPIN (Traction Sufficient)",
        "excess_force_N": margin,
    }


def calculate_traction_factor(
    f_max: float,
    weight: float,
) -> float:
    """
    Formula 26: Traction factor (page 7)
    k = F_max / W

    Args:
        f_max: Maximum tractive force in N
        weight: Total vehicle weight W in N

    Returns:
        Traction factor k (dimensionless)
    """
    if weight <= 0:
        raise ValueError("Weight must be positive.")
    return f_max / weight


def calculate_gradeability(
    traction_factor: float,
    rolling_resistance_coeff: float = ROLLING_RESISTANCE_COEFFICIENT,
) -> Dict[str, float]:
    """
    Formulas 27 & 28: Gradeability angle and gradient percentage (page 7)
    theta = sin^-1(k / sqrt(1 + f_r^2)) - tan^-1(f_r)  [in radians]
    G = 100 * tan(theta)                              [in percent]

    Args:
        traction_factor: Traction factor k
        rolling_resistance_coeff: Rolling resistance coefficient f_r

    Returns:
        Dict with angle in radians, angle in degrees, and gradient percentage.
    """
    hypot_val = math.sqrt(1.0 + (rolling_resistance_coeff ** 2))
    ratio = traction_factor / hypot_val

    if ratio > 1.0 or ratio < -1.0:
        raise ValueError(
            f"Traction factor / sqrt(1 + fr^2) = {ratio:.4f} is outside the domain [-1, 1] of arcsin."
        )

    theta_rad = math.asin(ratio) - math.atan(rolling_resistance_coeff)
    theta_deg = math.degrees(theta_rad)
    gradient_percent = 100.0 * math.tan(theta_rad)

    return {
        "gradeability_angle_rad": theta_rad,
        "gradeability_angle_deg": theta_deg,
        "gradient_percent": gradient_percent,
    }


def calculate_longitudinal_load_transfer(
    f_max: float,
    cg_height: float = CG_HEIGHT,
    wheelbase: float = WHEELBASE,
) -> float:
    """
    Formula 29: Longitudinal load transfer (page 7)
    Delta_W = (F_max * h) / L

    Args:
        f_max: Maximum tractive force F_max in N
        cg_height: Centre of gravity height h in m
        wheelbase: Wheelbase L in m

    Returns:
        Delta_W in Newtons (N)
    """
    if wheelbase <= 0:
        raise ValueError("Wheelbase must be positive.")
    return (f_max * cg_height) / wheelbase


def calculate_dynamic_front_axle_load(
    static_front_load: float,
    delta_w: float,
) -> float:
    """
    Formula 30: Dynamic front axle load (page 7)
    W_f_dyn = W_f - Delta_W

    Args:
        static_front_load: Static front axle load W_f in N
        delta_w: Longitudinal load transfer Delta_W in N

    Returns:
        W_f_dyn in Newtons (N)
    """
    return static_front_load - delta_w


def calculate_tyre_slip_torque(
    dynamic_front_load: float,
    dynamic_radius: float,
    mu: float = TYRE_ROAD_ADHESION,
    eta_contact: float = 1.0,
) -> float:
    """
    Formula 31: Tyre slip torque (page 7)
    T_slip = eta * mu * W_f_dyn * r

    Args:
        dynamic_front_load: Dynamic front axle load W_f_dyn in N
        dynamic_radius: Dynamic rolling radius r in m
        mu: Tyre-road adhesion coefficient mu
        eta_contact: Contact efficiency eta (default: 1.0)

    Returns:
        Tyre slip torque T_slip in Newton-metres (Nm)
    """
    if dynamic_radius <= 0:
        raise ValueError("Dynamic rolling radius must be positive.")
    return eta_contact * mu * dynamic_front_load * dynamic_radius


def compare_torque_demand_and_slip_torque(
    wheel_torque_demand: float,
    slip_torque: float,
) -> Dict[str, bool | str | float]:
    """
    Formula 32: Compare wheel torque demand and slip torque (page 7)
    Reuses Formula 10 and Formula 31.
    Reports whether wheel torque demand exceeds calculated slip torque.

    Args:
        wheel_torque_demand: T_demand = F_TW * r (Nm)
        slip_torque: T_slip (Nm)

    Returns:
        Dict indicating whether slip torque is exceeded and torque margin.
    """
    exceeds_slip = wheel_torque_demand > slip_torque
    margin = wheel_torque_demand - slip_torque
    return {
        "exceeds_slip_torque": exceeds_slip,
        "wheel_torque_demand_Nm": wheel_torque_demand,
        "slip_torque_Nm": slip_torque,
        "excess_torque_Nm": margin,
        "status": "SLIP TORQUE EXCEEDED (Driven wheels spin)" if exceeds_slip else "TRACTION MAINTAINED",
    }


def perform_complete_traction_analysis(
    weight: float,
    dynamic_radius: float,
    tractive_effort_1st_gear: float,
    wheelbase: float = WHEELBASE,
    cg_height: float = CG_HEIGHT,
    mu: float = TYRE_ROAD_ADHESION,
    rolling_resistance_coeff: float = ROLLING_RESISTANCE_COEFFICIENT,
    front_weight_share: float = None,
) -> Dict[str, any]:
    """
    Performs complete traction and gradeability analysis for a given vehicle mass.
    Reuses formulas 22-32 without duplicate implementations.
    """
    l1, l2 = calculate_cg_reference_distances(
        wheelbase,
        front_weight_share if front_weight_share is not None else 0.61
    )
    static_loads = calculate_static_axle_loads(weight, wheelbase, l1=l1, l2=l2)
    w_f = static_loads["W_f"]
    w_r = static_loads["W_r"]

    f_max = calculate_max_tractive_force_fwd(weight, l2, wheelbase, cg_height, mu)
    spin_check = check_wheel_spin(tractive_effort_1st_gear, f_max)
    k_traction = calculate_traction_factor(f_max, weight)
    gradeability = calculate_gradeability(k_traction, rolling_resistance_coeff)

    delta_w = calculate_longitudinal_load_transfer(f_max, cg_height, wheelbase)
    w_f_dyn = calculate_dynamic_front_axle_load(w_f, delta_w)
    t_slip = calculate_tyre_slip_torque(w_f_dyn, dynamic_radius, mu, eta_contact=1.0)

    # Torque demand in 1st gear
    t_demand_1st = calculate_wheel_torque_demand(tractive_effort_1st_gear, dynamic_radius)
    torque_comparison = compare_torque_demand_and_slip_torque(t_demand_1st, t_slip)

    return {
        "L1_m": l1,
        "L2_m": l2,
        "static_front_load_N": w_f,
        "static_rear_load_N": w_r,
        "f_max_N": f_max,
        "wheel_spin_1st_gear": spin_check,
        "traction_factor_k": k_traction,
        "gradeability": gradeability,
        "longitudinal_load_transfer_N": delta_w,
        "dynamic_front_load_N": w_f_dyn,
        "tyre_slip_torque_Nm": t_slip,
        "torque_demand_vs_slip": torque_comparison,
    }
