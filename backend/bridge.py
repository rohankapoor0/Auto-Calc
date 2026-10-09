"""
Lightweight Local Python Bridge CLI.
Communicates via standard input / output (stdin/stdout) using JSON.
Zero HTTP frameworks, zero REST/FastAPI/Flask endpoints, zero network ports opened.

Commands:
- get_defaults: Returns default specifications and metadata from specifications.py
- get_profiles: Returns all supported car profiles with full metadata and specifications
- get_profile_specs: Returns the specification dictionary for a given profile ID
- calculate: Invokes calculator.run_full_vehicle_calculation with supplied specifications
- calculate_profile: Calculates directly for a profile ID with optional overrides
"""

import sys
import json
import traceback
from typing import Any, Dict, Optional

import specifications as spec
import calculator as calc
import vehicle_profiles as vp


def get_default_specs() -> Dict[str, Any]:
    """Extract default specifications with their metadata from specifications.py."""
    raw_specs = {
        "KERB_MASS": spec.KERB_MASS,
        "GROSS_VEHICLE_MASS": spec.GROSS_VEHICLE_MASS,
        "WHEELBASE": spec.WHEELBASE,
        "CG_HEIGHT": spec.CG_HEIGHT,
        "FRONT_WEIGHT_SHARE": spec.FRONT_WEIGHT_SHARE,
        "GRAVITY": spec.GRAVITY,
        "MAX_POWER_KW": spec.MAX_POWER_KW,
        "RATED_POWER_RPM": spec.RATED_POWER_RPM,
        "MAX_ENGINE_TORQUE": spec.MAX_ENGINE_TORQUE,
        "GEAR_RATIOS": spec.GEAR_RATIOS,
        "FINAL_DRIVE_RATIO": spec.FINAL_DRIVE_RATIO,
        "TRANSMISSION_EFFICIENCY": spec.TRANSMISSION_EFFICIENCY,
        "TYRE_RIM_DIAMETER_IN": spec.TYRE_RIM_DIAMETER_IN,
        "TYRE_WIDTH_MM": spec.TYRE_WIDTH_MM,
        "TYRE_ASPECT_RATIO": spec.TYRE_ASPECT_RATIO,
        "TYRE_DEFLECTION_FACTOR": spec.TYRE_DEFLECTION_FACTOR,
        "TYRE_ROAD_ADHESION": spec.TYRE_ROAD_ADHESION,
        "AIR_DENSITY": spec.AIR_DENSITY,
        "DRAG_COEFFICIENT": spec.DRAG_COEFFICIENT,
        "FRONTAL_AREA": spec.FRONTAL_AREA,
        "ROLLING_RESISTANCE_COEFFICIENT": spec.ROLLING_RESISTANCE_COEFFICIENT,
        "CLUTCH_OUTER_DIAMETER_MM": spec.CLUTCH_OUTER_DIAMETER_MM,
        "CLUTCH_INNER_DIAMETER_MM": spec.CLUTCH_INNER_DIAMETER_MM,
        "CLUTCH_FRICTION_COEFFICIENT": spec.CLUTCH_FRICTION_COEFFICIENT,
        "CLUTCH_FRICTION_SURFACES": spec.CLUTCH_FRICTION_SURFACES,
        "CLUTCH_SAFETY_FACTOR": spec.CLUTCH_SAFETY_FACTOR,
        "MINIMUM_TURNING_RADIUS": spec.MINIMUM_TURNING_RADIUS,
        "TRACK_WIDTH": spec.TRACK_WIDTH,
        "AWD_TEST_SPEED_MPS": spec.AWD_TEST_SPEED_MPS,
    }
    return {
        "values": raw_specs,
        "metadata": spec.SPECIFICATION_METADATA,
    }


def execute_calculation(specs_dict: Dict[str, Any], include_awd: bool = False) -> Dict[str, Any]:
    """Execute complete calculations through calculator.py using provided specs."""
    # Convert gear ratio keys to int if necessary
    gear_ratios = specs_dict.get("GEAR_RATIOS")
    if gear_ratios and isinstance(gear_ratios, dict):
        gear_ratios = {int(k): float(v) for k, v in gear_ratios.items()}
    elif gear_ratios is None:
        gear_ratios = None

    def _val(key: str, default: Optional[float] = None) -> Optional[float]:
        v = specs_dict.get(key)
        if v is None:
            return default
        try:
            return float(v)
        except (ValueError, TypeError):
            return default

    results = calc.run_full_vehicle_calculation(
        kerb_mass=_val("KERB_MASS"),
        gross_vehicle_mass=_val("GROSS_VEHICLE_MASS"),
        wheelbase=_val("WHEELBASE"),
        cg_height=_val("CG_HEIGHT"),
        front_weight_share=_val("FRONT_WEIGHT_SHARE"),
        gravity=_val("GRAVITY", spec.GRAVITY),
        max_power_kw=_val("MAX_POWER_KW"),
        rated_power_rpm=_val("RATED_POWER_RPM"),
        max_engine_torque=_val("MAX_ENGINE_TORQUE"),
        gear_ratios=gear_ratios,
        final_drive_ratio=_val("FINAL_DRIVE_RATIO"),
        transmission_efficiency=_val("TRANSMISSION_EFFICIENCY"),
        rim_diameter_in=_val("TYRE_RIM_DIAMETER_IN"),
        width_mm=_val("TYRE_WIDTH_MM"),
        aspect_ratio=_val("TYRE_ASPECT_RATIO"),
        deflection_factor=_val("TYRE_DEFLECTION_FACTOR"),
        tyre_road_adhesion=_val("TYRE_ROAD_ADHESION"),
        air_density=_val("AIR_DENSITY"),
        drag_coefficient=_val("DRAG_COEFFICIENT"),
        frontal_area=_val("FRONTAL_AREA"),
        rolling_resistance_coeff=_val("ROLLING_RESISTANCE_COEFFICIENT"),
        clutch_od_mm=_val("CLUTCH_OUTER_DIAMETER_MM"),
        clutch_id_mm=_val("CLUTCH_INNER_DIAMETER_MM"),
        clutch_friction_coeff=_val("CLUTCH_FRICTION_COEFFICIENT"),
        clutch_friction_surfaces=int(_val("CLUTCH_FRICTION_SURFACES")) if _val("CLUTCH_FRICTION_SURFACES") is not None else None,
        clutch_safety_factor=_val("CLUTCH_SAFETY_FACTOR"),
        include_awd=include_awd,
        awd_speed_mps=_val("AWD_TEST_SPEED_MPS"),
        turning_radius=_val("MINIMUM_TURNING_RADIUS"),
        track_width=_val("TRACK_WIDTH"),
    )
    return results


def process_request(req: Dict[str, Any]) -> Dict[str, Any]:
    cmd = req.get("command")
    if cmd == "get_defaults":
        return {"status": "success", "data": get_default_specs()}
    elif cmd == "get_profiles":
        return {
            "status": "success",
            "data": {
                "summary": vp.get_all_profiles_metadata(),
                "profiles": vp.VEHICLE_PROFILES,
            },
        }
    elif cmd == "get_profile_specs":
        profile_id = req.get("profile_id", "hyundai_creta_15_crdi_6mt")
        specs = vp.profile_to_specs_dict(profile_id)
        return {"status": "success", "data": specs}
    elif cmd == "calculate":
        specs = req.get("specifications", {})
        include_awd = bool(req.get("include_awd", False))
        res = execute_calculation(specs, include_awd)
        return {"status": "success", "data": res}
    elif cmd == "calculate_profile":
        profile_id = req.get("profile_id", "hyundai_creta_15_crdi_6mt")
        overrides = req.get("overrides", {})
        base_specs = vp.profile_to_specs_dict(profile_id)
        base_specs.update(overrides)
        include_awd = bool(req.get("include_awd", False))
        res = execute_calculation(base_specs, include_awd)
        return {"status": "success", "data": res}
    else:
        return {"status": "error", "message": f"Unknown command: '{cmd}'"}


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing bridge get_profiles:")
        profiles_meta = vp.get_all_profiles_metadata()
        print(f"Loaded {len(profiles_meta['profiles'])} profiles:")
        for p in profiles_meta["profiles"]:
            print(f" - {p['id']}: {p['name']} ({p['variant']})")
        print("Testing profile calculation for Brezza:")
        brezza_specs = vp.profile_to_specs_dict("maruti_suzuki_brezza_15_petrol_6mt")
        calc_res = execute_calculation(brezza_specs)
        print("Brezza weight:", calc_res["basic_calculations"]["kerb_weight"])
        print("Brivetrain status:", calc_res["drivetrain"]["status"])
        return

    # Read single JSON string from command line argument if passed, or from stdin
    if len(sys.argv) > 1:
        raw_input = sys.argv[1]
    else:
        raw_input = sys.stdin.read()

    try:
        req = json.loads(raw_input)
        response = process_request(req)
    except Exception as e:
        response = {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
        }

    # Output standard JSON to stdout
    print(json.dumps(response))


if __name__ == "__main__":
    main()
