"""
Technical specifications and default parameters for Hyundai Creta 1.5 U2 CRDi Diesel (6-speed manual, FWD).

Every parameter is explicitly labeled as either:
- 'SPECIFIED / GIVEN': Official manufacturer specification from the Creta Design Dossier.
- 'ASSUMED': Engineering assumption stated in the dossier or required for calculations.
"""

from typing import Dict

# ==========================================
# 1. VEHICLE MASS & DIMENSIONS
# ==========================================
# Kerb mass of vehicle (SPECIFIED / GIVEN)
KERB_MASS: float = 1550.0  # kg

# Gross Vehicle Mass (GVW) (SPECIFIED / GIVEN)
GROSS_VEHICLE_MASS: float = 1805.0  # kg

# Wheelbase (SPECIFIED / GIVEN)
WHEELBASE: float = 2.610  # m

# Centre of gravity height (ASSUMED in dossier)
CG_HEIGHT: float = 0.605  # m

# Front weight distribution ratio (sf) (SPECIFIED / GIVEN)
FRONT_WEIGHT_SHARE: float = 0.61  # dimensionless (61% front, 39% rear)

# Standard acceleration due to gravity (STANDARD CONSTANT)
GRAVITY: float = 9.81  # m/s^2


# ==========================================
# 2. POWERTRAIN SPECIFICATIONS
# ==========================================
# Maximum rated engine power (SPECIFIED / GIVEN)
MAX_POWER_KW: float = 85.3  # kW (approx 115 PS / 114 bhp)

# Engine speed at rated power (SPECIFIED / GIVEN)
RATED_POWER_RPM: float = 4000.0  # rpm

# Maximum engine torque plateau (SPECIFIED / GIVEN)
MAX_ENGINE_TORQUE: float = 250.0  # Nm (available across 1500 - 2750 rpm)

# Manual transmission gear ratios (SPECIFIED / GIVEN)
GEAR_RATIOS: Dict[int, float] = {
    1: 3.833,
    2: 2.143,
    3: 1.370,
    4: 1.036,
    5: 0.839,
    6: 0.727,
}

# Final drive ratio (SPECIFIED / GIVEN)
FINAL_DRIVE_RATIO: float = 4.0

# Transmission mechanical efficiency (ASSUMED in dossier)
TRANSMISSION_EFFICIENCY: float = 0.90  # 90%


# ==========================================
# 3. TYRE & WHEEL SPECIFICATIONS
# ==========================================
# Rim nominal diameter (SPECIFIED / GIVEN)
TYRE_RIM_DIAMETER_IN: float = 17.0  # inches

# Tyre section width (SPECIFIED / GIVEN)
TYRE_WIDTH_MM: float = 215.0  # mm

# Tyre aspect ratio (SPECIFIED / GIVEN)
TYRE_ASPECT_RATIO: float = 55.0  # percent (215/55 R17)

# Tyre radial deflection factor under load fd (ASSUMED in dossier)
TYRE_DEFLECTION_FACTOR: float = 0.97  # dimensionless (dynamic rolling radius = 0.97 * free radius)

# Tyre-road adhesion / friction coefficient mu (ASSUMED in dossier)
TYRE_ROAD_ADHESION: float = 0.80  # dry asphalt friction


# ==========================================
# 4. ROAD RESISTANCE & ENVIRONMENT
# ==========================================
# Ambient air density rho (ASSUMED standard sea-level)
AIR_DENSITY: float = 1.225  # kg/m^3

# Aerodynamic drag coefficient Cd (ASSUMED in dossier)
DRAG_COEFFICIENT: float = 0.35

# Vehicle frontal area A (ASSUMED in dossier)
FRONTAL_AREA: float = 2.4  # m^2

# Tyre rolling resistance coefficient fr (ASSUMED in dossier)
ROLLING_RESISTANCE_COEFFICIENT: float = 0.015


# ==========================================
# 5. CLUTCH SYSTEM SPECIFICATIONS
# ==========================================
# Clutch disc outer diameter (SPECIFIED / GIVEN in dossier)
CLUTCH_OUTER_DIAMETER_MM: float = 240.0  # mm

# Clutch disc inner diameter (SPECIFIED / GIVEN in dossier)
CLUTCH_INNER_DIAMETER_MM: float = 155.0  # mm

# Clutch lining friction coefficient (ASSUMED in dossier)
CLUTCH_FRICTION_COEFFICIENT: float = 0.35

# Number of active friction surfaces n (SPECIFIED / GIVEN: single-plate dry clutch)
CLUTCH_FRICTION_SURFACES: int = 2

# Clutch design torque safety factor SF (SPECIFIED / GIVEN)
CLUTCH_SAFETY_FACTOR: float = 1.25


# ==========================================
# 6. HYPOTHETICAL AWD GEOMETRY & DYNAMICS
# ==========================================
# Minimum turning radius of outer front wheel Ro (SPECIFIED / GIVEN)
MINIMUM_TURNING_RADIUS: float = 5.3  # m

# Wheel track width t (ASSUMED for hypothetical AWD study)
TRACK_WIDTH: float = 1.55  # m

# Hypothetical cornering test speed V (ASSUMED in dossier worked example)
AWD_TEST_SPEED_MPS: float = 3.32  # m/s (~ 12 km/h)


# ==========================================
# PARAMETER ORIGIN REGISTRY (Metadata)
# ==========================================
SPECIFICATION_METADATA = {
    "KERB_MASS": {"value": KERB_MASS, "unit": "kg", "status": "SPECIFIED / GIVEN"},
    "GROSS_VEHICLE_MASS": {"value": GROSS_VEHICLE_MASS, "unit": "kg", "status": "SPECIFIED / GIVEN"},
    "MAX_POWER_KW": {"value": MAX_POWER_KW, "unit": "kW", "status": "SPECIFIED / GIVEN"},
    "RATED_POWER_RPM": {"value": RATED_POWER_RPM, "unit": "rpm", "status": "SPECIFIED / GIVEN"},
    "MAX_ENGINE_TORQUE": {"value": MAX_ENGINE_TORQUE, "unit": "Nm", "status": "SPECIFIED / GIVEN"},
    "WHEELBASE": {"value": WHEELBASE, "unit": "m", "status": "SPECIFIED / GIVEN"},
    "TYRE_RIM_DIAMETER_IN": {"value": TYRE_RIM_DIAMETER_IN, "unit": "inch", "status": "SPECIFIED / GIVEN"},
    "TYRE_WIDTH_MM": {"value": TYRE_WIDTH_MM, "unit": "mm", "status": "SPECIFIED / GIVEN"},
    "TYRE_ASPECT_RATIO": {"value": TYRE_ASPECT_RATIO, "unit": "%", "status": "SPECIFIED / GIVEN"},
    "TYRE_DEFLECTION_FACTOR": {"value": TYRE_DEFLECTION_FACTOR, "unit": "-", "status": "ASSUMED"},
    "GEAR_RATIOS": {"value": GEAR_RATIOS, "unit": "-", "status": "SPECIFIED / GIVEN"},
    "FINAL_DRIVE_RATIO": {"value": FINAL_DRIVE_RATIO, "unit": "-", "status": "SPECIFIED / GIVEN"},
    "TRANSMISSION_EFFICIENCY": {"value": TRANSMISSION_EFFICIENCY, "unit": "-", "status": "ASSUMED"},
    "AIR_DENSITY": {"value": AIR_DENSITY, "unit": "kg/m^3", "status": "ASSUMED"},
    "DRAG_COEFFICIENT": {"value": DRAG_COEFFICIENT, "unit": "-", "status": "ASSUMED"},
    "FRONTAL_AREA": {"value": FRONTAL_AREA, "unit": "m^2", "status": "ASSUMED"},
    "ROLLING_RESISTANCE_COEFFICIENT": {"value": ROLLING_RESISTANCE_COEFFICIENT, "unit": "-", "status": "ASSUMED"},
    "TYRE_ROAD_ADHESION": {"value": TYRE_ROAD_ADHESION, "unit": "-", "status": "ASSUMED"},
    "FRONT_WEIGHT_SHARE": {"value": FRONT_WEIGHT_SHARE, "unit": "-", "status": "SPECIFIED / GIVEN"},
    "CG_HEIGHT": {"value": CG_HEIGHT, "unit": "m", "status": "ASSUMED"},
    "GRAVITY": {"value": GRAVITY, "unit": "m/s^2", "status": "STANDARD CONSTANT"},
    "CLUTCH_OUTER_DIAMETER_MM": {"value": CLUTCH_OUTER_DIAMETER_MM, "unit": "mm", "status": "SPECIFIED / GIVEN"},
    "CLUTCH_INNER_DIAMETER_MM": {"value": CLUTCH_INNER_DIAMETER_MM, "unit": "mm", "status": "SPECIFIED / GIVEN"},
    "CLUTCH_FRICTION_COEFFICIENT": {"value": CLUTCH_FRICTION_COEFFICIENT, "unit": "-", "status": "ASSUMED"},
    "CLUTCH_FRICTION_SURFACES": {"value": CLUTCH_FRICTION_SURFACES, "unit": "-", "status": "SPECIFIED / GIVEN"},
    "CLUTCH_SAFETY_FACTOR": {"value": CLUTCH_SAFETY_FACTOR, "unit": "-", "status": "SPECIFIED / GIVEN"},
    "MINIMUM_TURNING_RADIUS": {"value": MINIMUM_TURNING_RADIUS, "unit": "m", "status": "SPECIFIED / GIVEN"},
    "TRACK_WIDTH": {"value": TRACK_WIDTH, "unit": "m", "status": "ASSUMED"},
    "AWD_TEST_SPEED_MPS": {"value": AWD_TEST_SPEED_MPS, "unit": "m/s", "status": "ASSUMED"},
}
