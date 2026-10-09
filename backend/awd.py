"""
Module F: Hypothetical AWD Extension (Formulas 44 - 70)
Implements hypothetical all-wheel-drive steering kinematics, cornering load transfer,
individual wheel normal loads, friction ellipse traction limits, and differential torque
distribution models (Open, 60:40 Fixed, Locked Centre, Ideal Torque-Vectoring)
according to pages 9-10 of the Creta Design Dossier.

NOTE: This is an optional exploratory analysis and is kept completely separate
from standard FWD production calculations.
"""

import math
from typing import Dict

from specifications import (
    TRACK_WIDTH,
    MINIMUM_TURNING_RADIUS,
    WHEELBASE,
    FRONT_WEIGHT_SHARE,
    CG_HEIGHT,
    TYRE_ROAD_ADHESION,
    GRAVITY,
    AWD_TEST_SPEED_MPS,
)
from basic_calculations import calculate_cg_reference_distances, calculate_vehicle_weight
from traction import calculate_static_axle_loads


def calculate_rear_axle_center_radius(
    outer_turning_radius: float = MINIMUM_TURNING_RADIUS,
    wheelbase: float = WHEELBASE,
    track_width: float = TRACK_WIDTH,
) -> float:
    """
    Formula 44: Rear axle centre radius (page 9)
    R_r = sqrt(R_o^2 - L^2) - (t / 2)

    Args:
        outer_turning_radius: Turning radius of outer front wheel R_o in m (default 5.3)
        wheelbase: Wheelbase L in m (default 2.61)
        track_width: Track width t in m (default 1.55)

    Returns:
        R_r in metres (m)
    """
    radicand = (outer_turning_radius ** 2) - (wheelbase ** 2)
    if radicand < 0:
        raise ValueError(
            f"Invalid geometry: Ro^2 ({outer_turning_radius**2:.3f}) < L^2 ({wheelbase**2:.3f})"
        )
    return math.sqrt(radicand) - (track_width / 2.0)


def calculate_front_inner_wheel_path_radius(
    r_rear: float,
    wheelbase: float = WHEELBASE,
    track_width: float = TRACK_WIDTH,
) -> float:
    """
    Formula 45: Front inner wheel path radius (page 9)
    R_FI = sqrt((R_r - t/2)^2 + L^2)

    Implemented exactly as stated in the dossier.

    Args:
        r_rear: Rear axle center radius R_r in m
        wheelbase: Wheelbase L in m
        track_width: Track width t in m

    Returns:
        R_FI in metres (m)
    """
    inner_term = r_rear - (track_width / 2.0)
    return math.sqrt((inner_term ** 2) + (wheelbase ** 2))


def calculate_rear_outer_wheel_path_radius(
    r_rear: float,
    wheelbase: float = WHEELBASE,
) -> float:
    """
    Formula 46: Rear outer wheel path radius (page 9)
    R_RO = sqrt(R_r^2 + L^2)

    Implemented exactly as stated in the dossier.

    Args:
        r_rear: Rear axle center radius R_r in m
        wheelbase: Wheelbase L in m

    Returns:
        R_RO in metres (m)
    """
    return math.sqrt((r_rear ** 2) + (wheelbase ** 2))


def calculate_rear_inner_wheel_path_radius(
    r_rear: float,
    track_width: float = TRACK_WIDTH,
) -> float:
    """
    Formula 47: Rear inner wheel path radius (page 9)
    R_RI = R_r - (t / 2)

    Args:
        r_rear: Rear axle center radius R_r in m
        track_width: Track width t in m

    Returns:
        R_RI in metres (m)
    """
    return r_rear - (track_width / 2.0)


def calculate_outer_steering_angle(
    r_rear: float,
    wheelbase: float = WHEELBASE,
) -> Dict[str, float]:
    """
    Formula 48: Outer steering angle (page 9)
    delta_o = tan^-1(L / R_r)

    Args:
        r_rear: Rear axle center radius R_r in m
        wheelbase: Wheelbase L in m

    Returns:
        Dict with angle in radians and degrees
    """
    if r_rear == 0:
        raise ValueError("Rear axle radius R_r cannot be zero.")
    delta_rad = math.atan(wheelbase / r_rear)
    return {
        "angle_rad": delta_rad,
        "angle_deg": math.degrees(delta_rad),
    }


def calculate_inner_steering_angle(
    r_rear: float,
    wheelbase: float = WHEELBASE,
    track_width: float = TRACK_WIDTH,
) -> Dict[str, float]:
    """
    Formula 49: Inner steering angle (page 9)
    delta_i = tan^-1(L / (R_r - t/2))

    Args:
        r_rear: Rear axle center radius R_r in m
        wheelbase: Wheelbase L in m
        track_width: Track width t in m

    Returns:
        Dict with angle in radians and degrees
    """
    denom = r_rear - (track_width / 2.0)
    if denom == 0:
        raise ValueError("Denominator (R_r - t/2) cannot be zero.")
    delta_rad = math.atan(wheelbase / denom)
    return {
        "angle_rad": delta_rad,
        "angle_deg": math.degrees(delta_rad),
    }


def calculate_cg_turning_radius(
    r_rear: float,
    l2: float,
) -> float:
    """
    Formula 50: CG turning radius (page 9)
    R_CG = sqrt(R_r^2 + L_2^2)

    Args:
        r_rear: Rear axle center radius R_r in m
        l2: Distance from rear axle to CG in m

    Returns:
        R_CG in metres (m)
    """
    return math.sqrt((r_rear ** 2) + (l2 ** 2))


def calculate_yaw_rate(
    speed_mps: float,
    r_cg: float,
) -> float:
    """
    Formula 51: Yaw rate (page 9)
    Omega = V / R_CG

    Args:
        speed_mps: Cornering vehicle speed V in m/s
        r_cg: CG turning radius R_CG in m

    Returns:
        Yaw rate Omega in rad/s
    """
    if r_cg <= 0:
        raise ValueError("CG turning radius must be positive.")
    return speed_mps / r_cg


def calculate_wheel_rotational_speed(
    yaw_rate: float,
    wheel_path_radius: float,
    dynamic_radius: float,
) -> float:
    """
    Formula 52: Wheel rotational speed (page 9)
    N_w = Omega * (R_w / r) * (60 / (2 * pi))

    Args:
        yaw_rate: Yaw rate Omega in rad/s
        wheel_path_radius: Path radius for specific wheel R_w in m
        dynamic_radius: Dynamic tyre rolling radius r in m

    Returns:
        Wheel rotational speed N_w in rpm
    """
    if dynamic_radius <= 0:
        raise ValueError("Dynamic rolling radius must be positive.")
    speed_w = yaw_rate * wheel_path_radius
    omega_w = speed_w / dynamic_radius
    n_w_rpm = omega_w * (60.0 / (2.0 * math.pi))
    return n_w_rpm


def calculate_lateral_acceleration(
    speed_mps: float,
    r_cg: float,
) -> float:
    """
    Formula 53: Lateral acceleration (page 9)
    a_y = V^2 / R_CG

    Args:
        speed_mps: Speed V in m/s
        r_cg: R_CG in m

    Returns:
        Lateral acceleration a_y in m/s^2
    """
    if r_cg <= 0:
        raise ValueError("CG turning radius must be positive.")
    return (speed_mps ** 2) / r_cg


def calculate_lateral_load_transfer_factor(
    lateral_accel: float,
    cg_height: float = CG_HEIGHT,
    track_width: float = TRACK_WIDTH,
    g: float = GRAVITY,
) -> float:
    """
    Formula 54: Lateral load-transfer factor (page 9)
    lambda = (a_y / g) * (h / t)

    Args:
        lateral_accel: a_y in m/s^2
        cg_height: h in m
        track_width: t in m
        g: gravity in m/s^2

    Returns:
        Load transfer factor lambda (dimensionless)
    """
    if track_width <= 0 or g <= 0:
        raise ValueError("Track width and gravity must be positive.")
    return (lateral_accel / g) * (cg_height / track_width)


def calculate_axle_lateral_load_transfers(
    w_f: float,
    w_r: float,
    lambda_factor: float,
) -> Dict[str, float]:
    """
    Formulas 55 & 56: Front and rear axle lateral load transfer (page 9)
    Delta_F_z,f = W_f * lambda
    Delta_F_z,r = W_r * lambda

    Args:
        w_f: Static front axle load in N
        w_r: Static rear axle load in N
        lambda_factor: Lateral load-transfer factor lambda

    Returns:
        Dict with Delta_F_zf and Delta_F_zr in Newtons
    """
    return {
        "Delta_F_zf": w_f * lambda_factor,
        "Delta_F_zr": w_r * lambda_factor,
    }


def calculate_individual_wheel_vertical_loads(
    w_f: float,
    w_r: float,
    delta_f_zf: float,
    delta_f_zr: float,
) -> Dict[str, float]:
    """
    Formulas 57 - 60: Individual wheel normal loads during steady cornering (page 9)
    F_z,FO = (W_f / 2) + Delta_F_z,f
    F_z,FI = (W_f / 2) - Delta_F_z,f
    F_z,RO = (W_r / 2) + Delta_F_z,r
    F_z,RI = (W_r / 2) - Delta_F_z,r

    Args:
        w_f: Static front axle load in N
        w_r: Static rear axle load in N
        delta_f_zf: Front lateral load transfer in N
        delta_f_zr: Rear lateral load transfer in N

    Returns:
        Dict with F_z_FO, F_z_FI, F_z_RO, F_z_RI in Newtons
    """
    return {
        "F_z_FO": (w_f / 2.0) + delta_f_zf,
        "F_z_FI": (w_f / 2.0) - delta_f_zf,
        "F_z_RO": (w_r / 2.0) + delta_f_zr,
        "F_z_RI": (w_r / 2.0) - delta_f_zr,
    }


def calculate_lateral_force_per_wheel(
    f_z: float,
    lateral_accel: float,
    g: float = GRAVITY,
) -> float:
    """
    Formula 61: Lateral force per wheel (page 10)
    F_y = F_z * (a_y / g)

    Args:
        f_z: Wheel vertical load in N
        lateral_accel: Lateral acceleration a_y in m/s^2
        g: gravity in m/s^2

    Returns:
        Lateral force F_y in Newtons (N)
    """
    if g <= 0:
        raise ValueError("Gravity must be positive.")
    return f_z * (lateral_accel / g)


def calculate_remaining_longitudinal_friction_coeff(
    mu: float = TYRE_ROAD_ADHESION,
    lateral_accel: float = 0.0,
    g: float = GRAVITY,
) -> float:
    """
    Formula 62: Remaining longitudinal friction coefficient (page 10)
    From friction circle / ellipse:
    mu_x = sqrt(mu^2 - (a_y / g)^2)

    Args:
        mu: Total tyre-road adhesion coefficient
        lateral_accel: Lateral acceleration a_y in m/s^2
        g: gravity in m/s^2

    Returns:
        Remaining longitudinal friction coefficient mu_x
    """
    if g <= 0:
        raise ValueError("Gravity must be positive.")
    lat_term = (lateral_accel / g) ** 2
    radicand = (mu ** 2) - lat_term
    if radicand < 0:
        raise ValueError(
            f"Tyre adhesion exceeded by lateral acceleration: (ay/g)^2 ({lat_term:.4f}) > mu^2 ({mu**2:.4f})"
        )
    return math.sqrt(radicand)


def calculate_max_longitudinal_force_per_wheel(
    f_z: float,
    mu_x: float,
) -> float:
    """
    Formula 63: Maximum longitudinal force per wheel (page 10)
    F_x,max = mu_x * F_z

    Args:
        f_z: Vertical wheel load in N
        mu_x: Available longitudinal friction coefficient

    Returns:
        F_x,max in Newtons (N)
    """
    return mu_x * f_z


def calculate_max_wheel_torque(
    f_x_max: float,
    dynamic_radius: float,
    eta_contact: float = 1.0,
) -> float:
    """
    Formula 64: Maximum torque per wheel (page 10)
    T_max = eta * mu_x * F_z * r = eta * F_x,max * r
    Using dossier's assumption eta = 1 at tyre contact.

    Args:
        f_x_max: Longitudinal force capacity in N
        dynamic_radius: Dynamic tyre radius r in m
        eta_contact: Contact efficiency (default 1.0)

    Returns:
        T_max in Newton-metres (Nm)
    """
    if dynamic_radius <= 0:
        raise ValueError("Dynamic radius must be positive.")
    return eta_contact * f_x_max * dynamic_radius


def calculate_ideal_total_torque_capacity(
    t_fo_max: float,
    t_fi_max: float,
    t_ro_max: float,
    t_ri_max: float,
) -> float:
    """
    Formula 65 & 69: Ideal total torque capacity (pages 10)
    T_ideal = T_FO,max + T_FI,max + T_RO,max + T_RI,max

    Returns:
        Total ideal torque capacity in Nm
    """
    return t_fo_max + t_fi_max + t_ro_max + t_ri_max


def calculate_open_differential_capacity(
    t_fo: float,
    t_fi: float,
    t_ro: float,
    t_ri: float,
) -> float:
    """
    Formula 66: Open differential AWD configuration (page 10)
    T_open = 4 * min(T_FO, T_FI, T_RO, T_RI)
    Limits all four wheels to weakest wheel's capacity.

    Returns:
        T_open in Newton-metres (Nm)
    """
    return 4.0 * min(t_fo, t_fi, t_ro, t_ri)


def calculate_fixed_60_40_center_diff_capacity(
    t_fo: float,
    t_fi: float,
    t_ro: float,
    t_ri: float,
) -> Dict[str, float | bool | str]:
    """
    Formula 67: Fixed 60:40 centre differential configuration (page 10)
    Uses dossier's method:
    T_rear,limit = 2 * min(T_RO, T_RI)
    T_total = T_rear,limit / 0.40
    T_front,per_wheel = (0.60 * T_total) / 2

    Checks whether the front axle wheels can support this allocated torque.
    If front capacity min(T_FO, T_FI) is insufficient, flags as traction-limited.

    Returns:
        Dict with total capacity, front per-wheel torque, rear per-wheel torque, and status.
    """
    t_rear_single_limit = min(t_ro, t_ri)
    t_rear_limit = 2.0 * t_rear_single_limit
    t_total_projected = t_rear_limit / 0.40
    t_front_per_wheel = (0.60 * t_total_projected) / 2.0

    # Front axle check
    t_front_single_limit = min(t_fo, t_fi)
    if t_front_per_wheel > t_front_single_limit:
        # Front axle slips before reaching 60:40 allocation
        t_front_limit = 2.0 * t_front_single_limit
        t_total_actual = t_front_limit / 0.60
        is_traction_limited = True
        status = "Front-axle traction limited (adjusted to front slip threshold)"
    else:
        t_total_actual = t_total_projected
        is_traction_limited = False
        status = "Nominal 60:40 distribution achieved"

    return {
        "t_total_Nm": t_total_actual,
        "t_rear_total_Nm": 0.40 * t_total_actual,
        "t_front_total_Nm": 0.60 * t_total_actual,
        "t_front_per_wheel_Nm": (0.60 * t_total_actual) / 2.0,
        "t_rear_per_wheel_Nm": (0.40 * t_total_actual) / 2.0,
        "is_traction_limited": is_traction_limited,
        "status": status,
    }


def calculate_locked_center_diff_capacity(
    t_fo: float,
    t_fi: float,
    t_ro: float,
    t_ri: float,
) -> Dict[str, float]:
    """
    Formula 68: Locked centre differential with open axle differentials (page 10)
    T_front = 2 * min(T_FO, T_FI)
    T_rear = 2 * min(T_RO, T_RI)
    T_locked = T_front + T_rear

    Returns:
        Dict with T_front, T_rear, and T_locked in Nm
    """
    t_front = 2.0 * min(t_fo, t_fi)
    t_rear = 2.0 * min(t_ro, t_ri)
    t_locked = t_front + t_rear
    return {
        "t_front_Nm": t_front,
        "t_rear_Nm": t_rear,
        "t_locked_Nm": t_locked,
    }


def calculate_percentage_of_ideal_capacity(
    t_config: float,
    t_ideal: float,
) -> float:
    """
    Formula 70: Percentage of ideal torque capacity (page 10)
    %ideal = (T_configuration / T_ideal) * 100

    Args:
        t_config: Torque capacity for specific differential layout in Nm
        t_ideal: Ideal total torque capacity in Nm

    Returns:
        Percentage of ideal capacity (%)
    """
    if t_ideal <= 0:
        raise ValueError("Ideal torque capacity must be positive.")
    return (t_config / t_ideal) * 100.0


def perform_complete_awd_analysis(
    dynamic_radius: float,
    mass_kg: float = 1550.0,
    speed_mps: float = AWD_TEST_SPEED_MPS,
    outer_turning_radius: float = MINIMUM_TURNING_RADIUS,
    track_width: float = TRACK_WIDTH,
    wheelbase: float = WHEELBASE,
    front_weight_share: float = FRONT_WEIGHT_SHARE,
    cg_height: float = CG_HEIGHT,
    mu: float = TYRE_ROAD_ADHESION,
    g: float = GRAVITY,
) -> Dict[str, any]:
    """
    Performs complete hypothetical AWD cornering, kinematics, and differential torque analysis.
    Explicitly documents all assumptions and retains dossier equations.
    """
    # 1. Basic vehicle forces
    weight = calculate_vehicle_weight(mass_kg, g)
    l1, l2 = calculate_cg_reference_distances(wheelbase, front_weight_share)
    static_loads = calculate_static_axle_loads(weight, wheelbase, l1=l1, l2=l2)
    w_f = static_loads["W_f"]
    w_r = static_loads["W_r"]

    # 2. Kinematics (Formulas 44 - 52)
    r_rear = calculate_rear_axle_center_radius(outer_turning_radius, wheelbase, track_width)
    r_fi = calculate_front_inner_wheel_path_radius(r_rear, wheelbase, track_width)
    r_ro = calculate_rear_outer_wheel_path_radius(r_rear, wheelbase)
    r_ri = calculate_rear_inner_wheel_path_radius(r_rear, track_width)
    delta_o = calculate_outer_steering_angle(r_rear, wheelbase)
    delta_i = calculate_inner_steering_angle(r_rear, wheelbase, track_width)
    r_cg = calculate_cg_turning_radius(r_rear, l2)

    yaw_rate = calculate_yaw_rate(speed_mps, r_cg)
    n_fo = calculate_wheel_rotational_speed(yaw_rate, outer_turning_radius, dynamic_radius)
    n_fi = calculate_wheel_rotational_speed(yaw_rate, r_fi, dynamic_radius)
    n_ro = calculate_wheel_rotational_speed(yaw_rate, r_ro, dynamic_radius)
    n_ri = calculate_wheel_rotational_speed(yaw_rate, r_ri, dynamic_radius)

    # 3. Cornering dynamics and load transfer (Formulas 53 - 60)
    a_y = calculate_lateral_acceleration(speed_mps, r_cg)
    lambda_factor = calculate_lateral_load_transfer_factor(a_y, cg_height, track_width, g)
    axle_transfers = calculate_axle_lateral_load_transfers(w_f, w_r, lambda_factor)
    wheel_loads = calculate_individual_wheel_vertical_loads(
        w_f, w_r, axle_transfers["Delta_F_zf"], axle_transfers["Delta_F_zr"]
    )

    # 4. Forces and torque capacities per wheel (Formulas 61 - 64)
    mu_x = calculate_remaining_longitudinal_friction_coeff(mu, a_y, g)
    fx_fo = calculate_max_longitudinal_force_per_wheel(wheel_loads["F_z_FO"], mu_x)
    fx_fi = calculate_max_longitudinal_force_per_wheel(wheel_loads["F_z_FI"], mu_x)
    fx_ro = calculate_max_longitudinal_force_per_wheel(wheel_loads["F_z_RO"], mu_x)
    fx_ri = calculate_max_longitudinal_force_per_wheel(wheel_loads["F_z_RI"], mu_x)

    t_fo_max = calculate_max_wheel_torque(fx_fo, dynamic_radius)
    t_fi_max = calculate_max_wheel_torque(fx_fi, dynamic_radius)
    t_ro_max = calculate_max_wheel_torque(fx_ro, dynamic_radius)
    t_ri_max = calculate_max_wheel_torque(fx_ri, dynamic_radius)

    # 5. Differential configurations (Formulas 65 - 70)
    t_ideal = calculate_ideal_total_torque_capacity(t_fo_max, t_fi_max, t_ro_max, t_ri_max)
    t_open = calculate_open_differential_capacity(t_fo_max, t_fi_max, t_ro_max, t_ri_max)
    diff_60_40 = calculate_fixed_60_40_center_diff_capacity(t_fo_max, t_fi_max, t_ro_max, t_ri_max)
    diff_locked = calculate_locked_center_diff_capacity(t_fo_max, t_fi_max, t_ro_max, t_ri_max)

    pct_open = calculate_percentage_of_ideal_capacity(t_open, t_ideal)
    pct_60_40 = calculate_percentage_of_ideal_capacity(diff_60_40["t_total_Nm"], t_ideal)
    pct_locked = calculate_percentage_of_ideal_capacity(diff_locked["t_locked_Nm"], t_ideal)

    return {
        "analysis_type": "Hypothetical AWD Extension (Optional)",
        "inputs": {
            "mass_kg": mass_kg,
            "speed_mps": speed_mps,
            "outer_turning_radius_m": outer_turning_radius,
            "track_width_m": track_width,
            "wheelbase_m": wheelbase,
            "mu": mu,
        },
        "kinematics": {
            "R_rear_m": r_rear,
            "R_FI_m": r_fi,
            "R_RO_m": r_ro,
            "R_RI_m": r_ri,
            "delta_outer_deg": delta_o["angle_deg"],
            "delta_inner_deg": delta_i["angle_deg"],
            "R_CG_m": r_cg,
            "yaw_rate_rad_s": yaw_rate,
            "wheel_speeds_rpm": {
                "front_outer": n_fo,
                "front_inner": n_fi,
                "rear_outer": n_ro,
                "rear_inner": n_ri,
            },
        },
        "dynamics": {
            "lateral_acceleration_m_s2": a_y,
            "lateral_load_transfer_factor_lambda": lambda_factor,
            "front_lateral_transfer_N": axle_transfers["Delta_F_zf"],
            "rear_lateral_transfer_N": axle_transfers["Delta_F_zr"],
            "wheel_vertical_loads_N": wheel_loads,
            "remaining_mu_x": mu_x,
            "wheel_max_longitudinal_forces_N": {
                "front_outer": fx_fo,
                "front_inner": fx_fi,
                "rear_outer": fx_ro,
                "rear_inner": fx_ri,
            },
            "wheel_max_torques_Nm": {
                "front_outer": t_fo_max,
                "front_inner": t_fi_max,
                "rear_outer": t_ro_max,
                "rear_inner": t_ri_max,
            },
        },
        "differential_comparison": {
            "ideal_total_torque_capacity_Nm": t_ideal,
            "open_differential": {
                "total_torque_Nm": t_open,
                "percentage_of_ideal": pct_open,
            },
            "fixed_60_40_center_differential": {
                "total_torque_Nm": diff_60_40["t_total_Nm"],
                "percentage_of_ideal": pct_60_40,
                "details": diff_60_40,
            },
            "locked_center_differential": {
                "total_torque_Nm": diff_locked["t_locked_Nm"],
                "percentage_of_ideal": pct_locked,
                "details": diff_locked,
            },
            "torque_vectoring_ideal": {
                "total_torque_Nm": t_ideal,
                "percentage_of_ideal": 100.0,
            },
        },
    }
