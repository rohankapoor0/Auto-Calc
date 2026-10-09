# Hyundai Creta 1.5 U2 CRDi Diesel - Vehicle Engineering Calculator

A pure Python calculation engine implementing all analytical formulas from the *Hyundai Creta Design Dossier* (1.5 U2 CRDi Diesel, 6-speed manual, FWD).

## 1. Project Structure

```text
vehicle-calculator/
└── backend/
    ├── main.py                  # Interactive CLI entrypoint
    ├── specifications.py        # Default vehicle parameters with origin metadata
    ├── basic_calculations.py    # Module A: Tyre geometry, weight, ratios, CG (Formulas 1-6)
    ├── drivetrain.py            # Module B: Tractive effort, speeds, torque demand (Formulas 7-10)
    ├── road_resistance.py       # Module C: Aerodynamic, rolling, grade resistance, power (Formulas 11-21)
    ├── traction.py              # Module D: Static/dynamic loads, FWD traction, gradeability (Formulas 22-32)
    ├── clutch.py                # Module E: Clutch geometry, clamping force, contact pressures (Formulas 33-43)
    ├── awd.py                   # Module F: Hypothetical AWD kinematics & differentials (Formulas 44-70)
    ├── calculator.py            # Master calculation orchestrator returning structured dicts
    ├── requirements.txt         # Dependencies (pytest)
    ├── README.md                # Engineering documentation
    └── tests/
        ├── test_basic_calculations.py
        ├── test_drivetrain.py
        ├── test_road_resistance.py
        ├── test_traction.py
        ├── test_clutch.py
        └── test_awd.py
```

## 2. Quickstart

### Prerequisites
- Python 3.11 or newer (tested with Python 3.12).
- Only third-party dependency is `pytest`.

### Installation
From the `vehicle-calculator/backend` directory:
```bash
pip install -r requirements.txt
```

### Running the Terminal Application
To run the interactive CLI menu:
```bash
python main.py
```

To run and display the complete vehicle analysis in one shot:
```bash
python main.py --all
```

### Running the Localhost React Frontend (Phase 2)
The frontend communicates directly with the Python calculation engine through a lightweight local process bridge (`bridge.py`) via stdio (standard input/output), without introducing FastAPI, Flask, or any external REST endpoints.

From the `vehicle-calculator/frontend` directory:
```bash
npm install
npm run dev
```
Then open:
👉 **[http://localhost:5173/](http://localhost:5173/)**

### Running the Test Suite
Run all backend unit and validation tests with `pytest`:
```bash
python -m pytest -v
```

All 37 test cases across all modules execute in `< 0.1s` with a 100% pass rate.

---

## 3. Supported Engineering Analyses

The engine is partitioned into 6 mathematical calculation modules (Modules A–F):

1. **Module A: Basic Calculations (`basic_calculations.py`)**
   - Free tyre radius $r_{\text{free}} = \frac{(D_{\text{rim}} \times 25.4 / 2) + (w \times AR / 100)}{1000} = 0.33415\text{ m}$
   - Dynamic rolling radius $r = f_d \cdot r_{\text{free}} = 0.32413\text{ m}$ ($f_d = 0.97$)
   - Vehicle weight $W = M \cdot g$ for Kerb (15,205.5 N) and GVW (17,707.1 N)
   - Overall gear ratios $i_o = i_g \cdot i_f$ across all 6 forward gears
   - Torque at rated power $T_P = \frac{P_{\max} \times 1000}{2\pi N_P / 60} = 203.64\text{ Nm}$ (at 4000 rpm)
   - CG reference distances $L_2 = s_f \cdot L = 1.5921\text{ m}$, $L_1 = L - L_2 = 1.0179\text{ m}$

2. **Module B: Drivetrain Calculations (`drivetrain.py`)**
   - Tractive effort $F_{TW} = \frac{T_e \cdot i_g \cdot i_f \cdot \eta_T}{r}$
   - Vehicle speed in m/s and km/h across 1500, 2750, and 4000 rpm
   - Rated power tractive effort at 4000 rpm using $T_P$ (203.64 Nm) rather than plateau torque (250 Nm)
   - Wheel torque demand $T_{\text{demand}} = F_{TW} \cdot r$

3. **Module C: Road Resistance & Power Demand (`road_resistance.py`)**
   - Air resistance constant $k = \frac{1}{2} \rho C_D A = 0.5145\text{ kg/m}$
   - Rolling resistance $R_{RR} = f_r \cdot W$
   - Aerodynamic resistance $R_{AF} = k V^2$
   - Grade resistance $R_{GR} = W \sin\theta$
   - Total road resistance $R_T = R_{RR} + R_{AF} + R_{GR}$
   - Drawbar pull $F_{db} = F_{TW} - R_T$
   - Wheel power $P_{\text{wheel}} = R_T \cdot V$ and engine power $P_{\text{engine}} = \frac{P_{\text{wheel}}}{\eta_T}$
   - Road resistance and power demand at 100 km/h:
     - Kerb: $R_T = 625.07\text{ N}$, $P_{\text{engine}} = 19.29\text{ kW}$
     - GVW: $R_T = 662.60\text{ N}$, $P_{\text{engine}} = 20.45\text{ kW}$
   - Top-speed feasibility check in 6th gear at 4000 rpm ($168.08\text{ km/h}$):
     - Kerb spare force $F_{db} = +294.73\text{ N}$ (Positive / Feasible)
     - GVW spare force $F_{db} = +257.20\text{ N}$ (Positive / Feasible)

4. **Module D: FWD Traction & Gradeability (`traction.py`)**
   - Static axle loads: $W_f = \frac{W L_2}{L}$, $W_r = \frac{W L_1}{L}$
   - Maximum FWD tractive force: $F_{\max} = \frac{\mu W L_2}{L + \mu h}$ ($6,259.5\text{ N}$ Kerb, $7,289.3\text{ N}$ GVW)
   - 1st gear wheel-spin condition: $F_{TW} > F_{\max}$ (Confirmed wheel spin occurs in 1st gear full throttle)
   - Traction factor $k = \frac{F_{\max}}{W} = 0.4117$
   - Maximum gradeability: $\theta = 23.45^\circ$, $G = 43.37\%$
   - Longitudinal dynamic load transfer $\Delta W = \frac{F_{\max} h}{L}$
   - Dynamic front axle load $W_{f,\text{dyn}} = W_f - \Delta W$
   - Tyre slip torque $T_{\text{slip}} = \eta \mu W_{f,\text{dyn}} r$ vs wheel torque demand $T_{\text{demand}}$

5. **Module E: Clutch Calculations (`clutch.py`)**
   - Friction radii: Outer $r_1 = 120.0\text{ mm}$, Inner $r_2 = 77.5\text{ mm}$, Mean $R = 98.75\text{ mm}$
   - Design torque: $T_c = SF \cdot T_e = 1.25 \times 250 = 312.5\text{ Nm}$
   - Clamping force (uniform wear): $W_c = \frac{T_c}{n \mu_c R} = 4,520.80\text{ N}$
   - Effective radius (uniform pressure): $R_{\text{eff}} = \frac{2}{3} \frac{r_1^3 - r_2^3}{r_1^2 - r_2^2} = 100.27\text{ mm}$
   - Torque capacity under uniform pressure: $T = 317.32\text{ Nm}$
   - Average contact pressure: $p_{\text{avg}} = \frac{W_c}{\pi (r_1^2 - r_2^2)} = 0.1714\text{ MPa}$ ($171.4\text{ kPa}$)
   - Uniform wear constant $C = \frac{W_c}{2\pi (r_1 - r_2)} = 16,929.58\text{ N/m}$
   - Maximum contact pressure $p_{\max} = \frac{C}{r_2} = 0.2184\text{ MPa}$ ($218.4\text{ kPa}$)
   - Minimum contact pressure $p_{\min} = \frac{C}{r_1} = 0.1411\text{ MPa}$ ($141.1\text{ kPa}$)

6. **Module F: Hypothetical AWD Extension (`awd.py`)**
   - Separate, optional kinematic and differential torque transfer study.
   - Kinematic radii for tight turning ($R_o = 5.3\text{ m}$, $V = 3.32\text{ m/s}$):
     - Rear axle center radius: $R_r = 3.838\text{ m}$
     - Front inner radius: $R_{FI} = 4.024\text{ m}$
     - Rear outer radius: $R_{RO} = 4.641\text{ m}$
     - Rear inner radius: $R_{RI} = 3.063\text{ m}$
     - CG radius: $R_{CG} = 4.155\text{ m}$
   - Steering angles: Outer $\delta_o = 34.22^\circ$, Inner $\delta_i = 40.44^\circ$
   - Cornering lateral acceleration $a_y = 2.653\text{ m/s}^2$ ($0.27\text{ g}$)
   - Friction circle remaining longitudinal grip $\mu_x = \sqrt{\mu^2 - (a_y/g)^2} = 0.7529$
   - Differential configuration torque capacity:
     - 1. Ideal Torque Vectoring: $3,710.7\text{ Nm}$ ($100.0\%$)
     - 2. Open Differentials: $2,283.3\text{ Nm}$ ($61.5\%$ of ideal)
     - 3. Fixed 60:40 Centre Diff: $2,854.2\text{ Nm}$ ($76.9\%$ of ideal)
     - 4. Locked Centre Diff: $2,927.4\text{ Nm}$ ($78.9\%$ of ideal)

---

## 4. Technical Specifications & Origin Labels

All parameters are cataloged in `specifications.py` with origin metadata:

| Parameter | Symbol | Value | Unit | Status | Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| Kerb Mass | $M_{\text{kerb}}$ | 1550.0 | kg | SPECIFIED / GIVEN | Official Creta 1.5 CRDi |
| Gross Vehicle Mass | $M_{\text{GVW}}$ | 1805.0 | kg | SPECIFIED / GIVEN | Fully laden mass |
| Wheelbase | $L$ | 2.610 | m | SPECIFIED / GIVEN | Manufacturer wheelbase |
| Centre of Gravity Height | $h$ | 0.605 | m | ASSUMED | Estimated in dossier |
| Front Weight Share | $s_f$ | 0.61 | - | SPECIFIED / GIVEN | 61% front / 39% rear |
| Max Engine Power | $P_{\max}$ | 85.3 | kW | SPECIFIED / GIVEN | 115 PS @ 4000 rpm |
| Rated Power Speed | $N_P$ | 4000.0 | rpm | SPECIFIED / GIVEN | Engine rated speed |
| Max Engine Torque | $T_e$ | 250.0 | Nm | SPECIFIED / GIVEN | 1500–2750 rpm plateau |
| Gear Ratios (1st to 6th) | $i_g$ | 3.833, 2.143, 1.370, 1.036, 0.839, 0.727 | - | SPECIFIED / GIVEN | 6-speed manual transmission |
| Final Drive Ratio | $i_f$ | 4.0 | - | SPECIFIED / GIVEN | Differential ratio |
| Transmission Efficiency | $\eta_T$ | 0.90 | - | ASSUMED | Drivetrain mechanical losses |
| Tyre Specification | - | 215/55 R17 | - | SPECIFIED / GIVEN | Width 215 mm, AR 55%, Rim 17" |
| Tyre Deflection Factor | $f_d$ | 0.97 | - | ASSUMED | Radial deformation under load |
| Road Adhesion Coefficient | $\mu$ | 0.80 | - | ASSUMED | Dry asphalt |
| Air Density | $\rho$ | 1.225 | kg/m³ | ASSUMED | Sea-level ambient standard |
| Drag Coefficient | $C_D$ | 0.35 | - | ASSUMED | SUV aerodynamic profile |
| Frontal Area | $A$ | 2.40 | m² | ASSUMED | Front projected area |
| Rolling Resistance Coeff. | $f_r$ | 0.015 | - | ASSUMED | Radial tyres on tarmac |
| Clutch Outer Diameter | $OD$ | 240.0 | mm | SPECIFIED / GIVEN | Clutch disc friction face |
| Clutch Inner Diameter | $ID$ | 155.0 | mm | SPECIFIED / GIVEN | Clutch disc friction face |
| Clutch Friction Coeff. | $\mu_c$ | 0.35 | - | ASSUMED | Dry organic friction lining |
| Clutch Friction Faces | $n$ | 2 | - | SPECIFIED / GIVEN | Single plate dry clutch |
| Clutch Safety Factor | $SF$ | 1.25 | - | SPECIFIED / GIVEN | Design margin |
| Min Turning Radius | $R_o$ | 5.30 | m | SPECIFIED / GIVEN | Outer front wheel path |
| Track Width | $t$ | 1.55 | m | ASSUMED | Hypothetical AWD track |

---

## 5. Phase 3: Multi-Car Profiles & Specification Comparison

Phase 3 extends the engineering calculation engine with a local multi-car profile architecture and side-by-side vehicle comparison capability without adding external APIs, cloud services, or runtime web scrapers.

### Supported Vehicles & Powertrain Variants
1. **Hyundai Creta 1.5 U2 CRDi Diesel 6MT (2024, FWD)** — Reference vehicle from engineering dossier.
2. **Tata Nexon 1.2 Revotron Turbo Petrol 6MT (2024, FWD)** — Compact turbo-petrol SUV.
3. **Tata Nexon 1.5 Revotorq Diesel 6MT (2024, FWD)** — Compact turbo-diesel SUV.
4. **Maruti Suzuki Brezza 1.5 K15C Smart Hybrid Petrol 6MT (2024, FWD)** — Naturally aspirated hybrid petrol SUV.

### Data Integrity & Provenance
All parameters are locally stored with provenance metadata (`verified`, `assumed`, `unavailable`):
- **Verified values**: Sourced directly from official manufacturer brochures and technical specifications.
- **Assumed values**: Documented engineering assumptions (e.g. standard atmospheric density $\rho = 1.225\text{ kg/m}^3$, rolling resistance $f_r = 0.015$, tyre-road adhesion $\mu = 0.80$, manual transaxle efficiency $\eta_T = 0.90$).
- **Unavailable values**: Unreleased proprietary manufacturer data (e.g., individual gear ratios, final drive ratios, and clutch dimensions for Nexon and Brezza manual transmissions). These are mapped strictly to `null` (`None`) and their dependent calculations are disabled with clear diagnostic notices (`N/A — specification unavailable`) rather than fabricating values or borrowing Creta data.

### Side-by-Side Comparison
The UI provides a dedicated comparison view allowing 2 or 3 vehicles to be compared side-by-side across Engine, Transmission, Dimensions, Mass, and all calculated engineering outputs with metric units and provenance badges.

---

## 6. Engineering Verification & Formula Discrepancy Notes

1. **Clutch Effective Radius ($R_{\text{eff}}$)**:
   - Evaluated exactly as $R_{\text{eff}} = \frac{2}{3} \frac{0.120^3 - 0.0775^3}{0.120^2 - 0.0775^2} = 0.100274\text{ m} = 100.27\text{ mm}$.
   - Hand-rounded estimates in informal documents sometimes cite $100.15\text{ mm}$; the exact analytical formula is preserved.
2. **Formula 40 Contact Pressure**:
   - $p_{\text{avg}} = \frac{W_c}{\pi (r_1^2 - r_2^2)}$. The printed expression represents the clamping force over one annular friction surface, yielding $0.1714\text{ MPa}$.
3. **Hypothetical AWD Kinematics**:
   - Formulas 44–70 are strictly confined to the optional AWD module (`awd.py`) and do not modify the production FWD drivetrain specifications.
   - For ordinary FWD profiles (Nexon, Brezza), the AWD module is disabled by default.
   - For the 60:40 differential allocation, if the required front torque exceeds the physical front tyre traction limit, the model flags the configuration as traction-limited and clamps to the maximum deliverable torque.
