"""
Module E: Clutch Calculations (Formulas 33 - 43)
Implements clutch friction dimensions, design torque, axial clamping force (uniform wear),
effective radius and torque capacity (uniform pressure), contact pressures, and wear constants
according to the Creta Design Dossier.
"""

import math
from typing import Dict

from specifications import (
    CLUTCH_OUTER_DIAMETER_MM,
    CLUTCH_INNER_DIAMETER_MM,
    CLUTCH_FRICTION_COEFFICIENT,
    CLUTCH_FRICTION_SURFACES,
    CLUTCH_SAFETY_FACTOR,
    MAX_ENGINE_TORQUE,
)


def calculate_outer_friction_radius(outer_diameter_mm: float = CLUTCH_OUTER_DIAMETER_MM) -> float:
    """
    Formula 33: Outer friction radius (page 8)
    r_1 = OD / 2
    Converts diameter from mm to metres first: OD_m = OD_mm / 1000

    Args:
        outer_diameter_mm: Outer diameter in mm (default 240.0)

    Returns:
        r_1 in metres (m)
    """
    if outer_diameter_mm <= 0:
        raise ValueError("Clutch outer diameter must be positive.")
    od_m = outer_diameter_mm / 1000.0
    return od_m / 2.0


def calculate_inner_friction_radius(inner_diameter_mm: float = CLUTCH_INNER_DIAMETER_MM) -> float:
    """
    Formula 34: Inner friction radius (page 8)
    r_2 = ID / 2
    Converts diameter from mm to metres first: ID_m = ID_mm / 1000

    Args:
        inner_diameter_mm: Inner diameter in mm (default 155.0)

    Returns:
        r_2 in metres (m)
    """
    if inner_diameter_mm <= 0:
        raise ValueError("Clutch inner diameter must be positive.")
    id_m = inner_diameter_mm / 1000.0
    return id_m / 2.0


def calculate_mean_friction_radius(r1: float, r2: float) -> float:
    """
    Formula 35: Mean friction radius (page 8)
    R = (r_1 + r_2) / 2

    Args:
        r1: Outer friction radius in m
        r2: Inner friction radius in m

    Returns:
        Mean friction radius R in metres (m)
    """
    if r1 <= r2 or r2 <= 0:
        raise ValueError("Outer radius r1 must be greater than inner radius r2, and r2 > 0.")
    return (r1 + r2) / 2.0


def calculate_design_torque(
    engine_torque: float = MAX_ENGINE_TORQUE,
    safety_factor: float = CLUTCH_SAFETY_FACTOR,
) -> float:
    """
    Formula 36: Design torque (page 8)
    T_c = SF * T_e

    Args:
        engine_torque: Maximum engine torque T_e in Nm (default 250.0)
        safety_factor: Clutch safety factor SF (default 1.25)

    Returns:
        Clutch design torque T_c in Newton-metres (Nm)
    """
    if engine_torque < 0 or safety_factor <= 0:
        raise ValueError("Engine torque must be non-negative and safety factor must be positive.")
    return safety_factor * engine_torque


def calculate_axial_clamping_force(
    design_torque: float,
    mean_radius: float,
    friction_coefficient: float = CLUTCH_FRICTION_COEFFICIENT,
    friction_surfaces: int = CLUTCH_FRICTION_SURFACES,
) -> float:
    """
    Formula 37: Axial clamping force under uniform wear (page 8)
    From T_c = n * mu_c * W_c * R, rearranged as:
    W_c = T_c / (n * mu_c * R)

    Args:
        design_torque: Design torque T_c in Nm
        mean_radius: Mean friction radius R in m
        friction_coefficient: Clutch lining friction coefficient mu_c (default 0.35)
        friction_surfaces: Number of friction surfaces n (default 2)

    Returns:
        Axial clamping force W_c in Newtons (N)
    """
    denom = friction_surfaces * friction_coefficient * mean_radius
    if denom <= 0:
        raise ValueError("Denominator in clamping force calculation must be positive.")
    return design_torque / denom


def calculate_effective_radius_uniform_pressure(r1: float, r2: float) -> float:
    """
    Formula 38: Effective radius under uniform pressure (page 8)
    R_eff = (2 / 3) * ((r_1^3 - r_2^3) / (r_1^2 - r_2^2))

    Args:
        r1: Outer friction radius in m
        r2: Inner friction radius in m

    Returns:
        Effective friction radius R_eff in metres (m)
    """
    if r1 <= r2 or r2 <= 0:
        raise ValueError("Outer radius r1 must be strictly greater than inner radius r2.")
    num = (r1 ** 3) - (r2 ** 3)
    denom = (r1 ** 2) - (r2 ** 2)
    return (2.0 / 3.0) * (num / denom)


def calculate_torque_capacity_uniform_pressure(
    clamping_force: float,
    effective_radius: float,
    friction_coefficient: float = CLUTCH_FRICTION_COEFFICIENT,
    friction_surfaces: int = CLUTCH_FRICTION_SURFACES,
) -> float:
    """
    Formula 39: Torque capacity under uniform pressure (page 8)
    T = n * mu_c * W_c * R_eff

    Args:
        clamping_force: Axial clamping force W_c in N
        effective_radius: Effective radius R_eff in m
        friction_coefficient: mu_c
        friction_surfaces: n

    Returns:
        Torque capacity T in Newton-metres (Nm)
    """
    return friction_surfaces * friction_coefficient * clamping_force * effective_radius


def calculate_average_contact_pressure(
    clamping_force: float,
    r1: float,
    r2: float,
) -> float:
    """
    Formula 40: Average contact pressure (page 8)
    p_avg = W_c / (pi * (r_1^2 - r_2^2))

    NOTE FOR ENGINEERING VERIFICATION:
    This equation is printed in the dossier on page 8. It represents the axial clamping force
    divided by the annular contact area pi*(r_1^2 - r_2^2) of one friction face.
    Implemented exactly as specified.

    Args:
        clamping_force: W_c in N
        r1: Outer radius in m
        r2: Inner radius in m

    Returns:
        Average contact pressure in Pascals (Pa)
    """
    area = math.pi * ((r1 ** 2) - (r2 ** 2))
    if area <= 0:
        raise ValueError("Annular area must be positive.")
    return clamping_force / area


def calculate_uniform_wear_constant(
    clamping_force: float,
    r1: float,
    r2: float,
) -> float:
    """
    Formula 41: Uniform-wear pressure constant (page 8)
    C = W_c / (2 * pi * (r_1 - r_2))

    Args:
        clamping_force: W_c in N
        r1: Outer radius in m
        r2: Inner radius in m

    Returns:
        Uniform wear constant C in N/m
    """
    denom = 2.0 * math.pi * (r1 - r2)
    if denom <= 0:
        raise ValueError("Denominator (2 * pi * (r1 - r2)) must be positive.")
    return clamping_force / denom


def calculate_max_pressure_uniform_wear(
    c_constant: float,
    r2: float,
) -> float:
    """
    Formula 42: Maximum pressure under uniform wear (page 8)
    p_max = C / r_2
    (Occurs at the inner radius r_2)

    Args:
        c_constant: Uniform-wear constant C in N/m
        r2: Inner radius in m

    Returns:
        Maximum contact pressure in Pascals (Pa)
    """
    if r2 <= 0:
        raise ValueError("Inner radius r2 must be positive.")
    return c_constant / r2


def calculate_min_pressure_uniform_wear(
    c_constant: float,
    r1: float,
) -> float:
    """
    Formula 43: Minimum pressure under uniform wear (page 8)
    p_min = C / r_1
    (Occurs at the outer radius r_1)

    Args:
        c_constant: Uniform-wear constant C in N/m
        r1: Outer radius in m

    Returns:
        Minimum contact pressure in Pascals (Pa)
    """
    if r1 <= 0:
        raise ValueError("Outer radius r1 must be positive.")
    return c_constant / r1


def perform_complete_clutch_analysis(
    outer_diameter_mm: float = CLUTCH_OUTER_DIAMETER_MM,
    inner_diameter_mm: float = CLUTCH_INNER_DIAMETER_MM,
    engine_torque: float = MAX_ENGINE_TORQUE,
    safety_factor: float = CLUTCH_SAFETY_FACTOR,
    friction_coefficient: float = CLUTCH_FRICTION_COEFFICIENT,
    friction_surfaces: int = CLUTCH_FRICTION_SURFACES,
) -> Dict[str, float]:
    """
    Performs complete clutch calculations according to formulas 33-43.
    Pressures are reported in both Pa and MPa for presentation.
    """
    r1 = calculate_outer_friction_radius(outer_diameter_mm)
    r2 = calculate_inner_friction_radius(inner_diameter_mm)
    mean_r = calculate_mean_friction_radius(r1, r2)
    t_c = calculate_design_torque(engine_torque, safety_factor)
    w_c = calculate_axial_clamping_force(t_c, mean_r, friction_coefficient, friction_surfaces)

    r_eff = calculate_effective_radius_uniform_pressure(r1, r2)
    t_uniform_pressure = calculate_torque_capacity_uniform_pressure(
        w_c, r_eff, friction_coefficient, friction_surfaces
    )

    p_avg_pa = calculate_average_contact_pressure(w_c, r1, r2)
    c_const = calculate_uniform_wear_constant(w_c, r1, r2)
    p_max_pa = calculate_max_pressure_uniform_wear(c_const, r2)
    p_min_pa = calculate_min_pressure_uniform_wear(c_const, r1)

    return {
        "outer_radius_r1_m": r1,
        "inner_radius_r2_m": r2,
        "mean_radius_R_m": mean_r,
        "effective_radius_Reff_m": r_eff,
        "design_torque_Tc_Nm": t_c,
        "axial_clamping_force_Wc_N": w_c,
        "torque_capacity_uniform_pressure_Nm": t_uniform_pressure,
        "average_contact_pressure_Pa": p_avg_pa,
        "average_contact_pressure_MPa": p_avg_pa / 1e6,
        "uniform_wear_constant_C_Npm": c_const,
        "max_pressure_uniform_wear_Pa": p_max_pa,
        "max_pressure_uniform_wear_MPa": p_max_pa / 1e6,
        "min_pressure_uniform_wear_Pa": p_min_pa,
        "min_pressure_uniform_wear_MPa": p_min_pa / 1e6,
    }
