# AutoCalc - Vehicle Engineering & Dynamics Calculator

AutoCalc is a full-stack, high-precision vehicle engineering and dynamics simulation platform. It implements first-principles mathematical and kinematic formulations for drivetrain analysis, road load resistance, traction and weight transfer dynamics, clutch sizing and wear mechanics, and all-wheel-drive (AWD) kinematics.

The platform provides both an **interactive Python CLI** and a **modern, responsive web interface** built with React, TypeScript, and Vite. The web frontend communicates with the Python mathematical engine in real time using a direct stdio-based process bridge (no external API services or databases required).

---

## Table of Contents
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [How the Calculation Engine Works](#how-the-calculation-engine-works)
- [Prerequisites](#prerequisites)
- [Installation & How to Run](#installation--how-to-run)
  - [Option A: Running the Web Application (Interactive Dashboard)](#option-a-running-the-web-application-interactive-dashboard)
  - [Option B: Running the Python CLI Engine](#option-b-running-the-python-cli-engine)
  - [Option C: Running Automated Tests](#option-c-running-automated-tests)
- [Project Directory Structure](#project-directory-structure)
- [Supported Vehicle Profiles](#supported-vehicle-profiles)
- [License](#license)

---

## Key Features

1. **Precision Automotive Physics**:
   - **Module A: Basic Vehicle Geometry & Weights**: Calculates tyre dynamic rolling radius, effective gearing, CG distribution ($L_1$, $L_2$), and torque at rated engine speed.
   - **Module B: Drivetrain Dynamics**: Computes gear-by-gear tractive force curves ($F_{TW}$), speed sweeps (1500, 2750, 4000 rpm), and wheel torque demands.
   - **Module C: Road Resistances & Power Demand**: Aerodynamic drag ($R_{AF}$), rolling resistance ($R_{RR}$), grade resistance ($R_{GR}$), total resistance, drawbar pull, and wheel/engine power requirements up to 100+ km/h.
   - **Module D: Traction & Dynamic Load Transfer**: Computes dynamic front and rear normal forces under acceleration and braking, maximum traction limits ($\mu = 0.85$ dry asphalt / $\mu = 0.35$ wet/gravel), maximum tractive capacity, and maximum gradeability across all gears.
   - **Module E: Clutch Engineering**: Analyzes single-plate dry friction clutches (OD, ID, effective mean radius $R_m$), axial clamping load ($F_a$), Uniform Wear vs. Uniform Pressure torque capacities, and surface contact pressures ($p_{\text{mean}}$, $p_{\max}$).
   - **Module F: Hypothetical AWD Kinematics & Differentials**: Simulates open/locked differentials, torque distribution splits, inner vs. outer wheel turn radius geometry (Ackermann), and turn-slip kinematics.

2. **Pre-Loaded Vehicle Benchmarks**:
   - Includes real-world engineering profiles for **Hyundai Creta 1.5 CRDi Diesel**, **Hyundai Creta 1.5 MPi Petrol**, **Hyundai Tucson 2.0 CRDi AWD**, and **Hyundai i20 1.2 Kappa**.
   - Compare vehicle performance, gear step ratios, and gradeability side-by-side.

3. **Zero-Setup Communication Bridge**:
   - The Vite development server features a custom middleware plugin that calls `backend/bridge.py` via Python child process pipes (`stdio`).
   - Runs seamlessly on localhost without configuring reverse proxies, ASGI/WSGI servers, or REST endpoints.

---

## System Architecture

```text
┌────────────────────────────────────────────────────────┐
│             React / TypeScript Web Client              │
│  - Interactive parameter sliders & real-time updates   │
│  - Specification validation and constraint checking    │
│  - Comparison engine across multiple vehicle profiles  │
│  - Dynamic charts and formula accordions               │
└───────────────────────────┬────────────────────────────┘
                            │ POST /__bridge_rpc (JSON Payload)
                            ▼
┌────────────────────────────────────────────────────────┐
│               Vite Dev Server Bridge Plugin            │
│  - Intercepts requests in development middleware       │
│  - Spawns local Python process with arguments          │
└───────────────────────────┬────────────────────────────┘
                            │ stdin / stdout (JSON)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Python Calculation Core (backend/)         │
│  - bridge.py: CLI and JSON RPC dispatcher              │
│  - calculator.py: Master engine orchestrator           │
│  - basic_calculations.py, drivetrain.py,               │
│    road_resistance.py, traction.py, clutch.py, awd.py  │
│  - vehicle_profiles.py: Factory specs and benchmarks   │
└────────────────────────────────────────────────────────┘
```

---

## How the Calculation Engine Works

1. **Parameters & Inputs**: A baseline vehicle profile (e.g. Creta 1.5 CRDi) provides curb weight, gross vehicle weight (GVW), gear ratios, final drive, tyre dimensions (e.g. 205/65 R16), aerodynamic drag coefficient ($C_D$), frontal area ($A$), and engine torque curve.
2. **Dynamic Processing**:
   - In the frontend, users can adjust individual parameters (e.g., incline angle, speed, payload, tyre size, or road friction coefficient $\mu$).
   - The payload is dispatched to `backend/bridge.py` which instantiates the calculation modules.
3. **Structured Verification**:
   - Output includes step-by-step intermediate metrics, tractive effort curves, safety factors, and pass/fail thresholds for vehicle specifications (e.g., meeting minimum gradeability requirements).

---

## Prerequisites

Make sure the following runtimes are installed on your system:

- **Python**: Version `3.10` or higher (`python --version`)
- **Node.js**: Version `18.x` or higher (`node --version`)
- **npm**: Version `9.x` or higher (`npm --version`)
- **Git** (for cloning and version control)

---

## Installation & How to Run

Clone the repository to your local machine:
```bash
git clone https://github.com/rohankapoor0/Auto-Calc.git
cd Auto-Calc
```

### Option A: Running the Web Application (Interactive Dashboard)

1. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Development Server**:
   ```bash
   npm run dev
   ```

3. **Access the App**:
   Open your browser and navigate to:
   ```text
   http://localhost:5173
   ```
   *(The Vite dev server will automatically invoke the Python engine in `../backend/bridge.py` whenever you interact with calculations).*

---

### Option B: Running the Python CLI Engine

If you prefer to run or test the calculation engine directly in your terminal:

1. **Navigate to the Backend Directory**:
   ```bash
   cd backend
   ```

2. **Install Python Requirements (pytest)**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Full Analysis**:
   ```bash
   # Run full calculation suite and print comprehensive output
   python main.py --all
   ```

4. **Run Interactive Menu**:
   ```bash
   python main.py
   ```
   *Follow the on-screen terminal prompts to select individual modules (A through F).*

---

### Option C: Running Automated Tests

A comprehensive unit test suite validates every analytical formula against engineering reference outputs:

```bash
cd backend
python -m pytest -v
```

All 37 test cases cover:
- Module A: Tyre rolling radius and CG weight split
- Module B: Gear speeds and tractive force
- Module C: Aerodynamic drag and power demand at 100 km/h
- Module D: Dynamic weight transfer, traction limit, and gradeability
- Module E: Clutch clamping forces, torque capacities, and surface wear
- Module F: AWD differential kinematics and turn radiuses

---

## Project Directory Structure

```text
Auto-Calc/
├── README.md                     # Main repository documentation (this file)
├── .gitignore                    # Git ignore rules for node_modules, pycache, etc.
├── backend/                      # Pure Python vehicle calculation engine
│   ├── basic_calculations.py     # Module A: Geometry, tyre radius, ratios, CG
│   ├── drivetrain.py             # Module B: Tractive efforts, speeds, wheel torque
│   ├── road_resistance.py        # Module C: Aero, rolling, grade resistance, power
│   ├── traction.py               # Module D: Dynamic normal loads, traction, gradeability
│   ├── clutch.py                 # Module E: Clutch geometry, torque capacity, clamping
│   ├── awd.py                    # Module F: AWD kinematics, differentials, turn geometry
│   ├── calculator.py             # Master orchestrator combining all modules
│   ├── bridge.py                 # CLI/stdio JSON RPC bridge for the web app
│   ├── main.py                   # Terminal CLI application
│   ├── specifications.py         # Baseline vehicle specification dictionary
│   ├── vehicle_profiles.py       # Predefined multi-vehicle profiles (Creta, Tucson, i20)
│   ├── requirements.txt          # Python dependencies
│   ├── README.md                 # Detailed mathematical formulas & engineering derivations
│   └── tests/                    # Pytest test suite
│       ├── test_basic_calculations.py
│       ├── test_drivetrain.py
│       ├── test_road_resistance.py
│       ├── test_traction.py
│       ├── test_clutch.py
│       └── test_awd.py
└── frontend/                     # Modern React + TypeScript + Vite web interface
    ├── package.json              # Frontend package configuration
    ├── vite.config.ts            # Vite config with custom Python stdio bridge middleware
    ├── tsconfig.json             # TypeScript configuration
    ├── index.html                # Application HTML root
    └── src/
        ├── App.tsx               # Main application component & tab router
        ├── index.css             # Design system styling & responsive layout
        ├── types.ts              # TypeScript type definitions for vehicle specs
        ├── components/           # Reusable UI components (Headers, Sidebar, Accordions)
        ├── views/                # Module views (Overview, Basic, Drivetrain, Traction, etc.)
        ├── services/             # Bridge service calling the Python RPC
        └── data/                 # Vehicle profile definitions
```

---

## Supported Vehicle Profiles

| Parameter | Hyundai Creta 1.5 CRDi | Hyundai Creta 1.5 MPi | Hyundai Tucson 2.0 CRDi AWD | Hyundai i20 1.2 Kappa |
|---|---|---|---|---|
| **Engine Type** | 1.5L U2 CRDi Turbo Diesel | 1.5L Smartstream MPi Petrol | 2.0L R CRDi Turbo Diesel | 1.2L Kappa MPi Petrol |
| **Power** | 115 PS @ 4000 rpm | 115 PS @ 6300 rpm | 186 PS @ 4000 rpm | 83 PS @ 6000 rpm |
| **Max Torque** | 250 Nm @ 1500–2750 rpm | 144 Nm @ 4500 rpm | 400 Nm @ 1750–2750 rpm | 114.7 Nm @ 4200 rpm |
| **Transmission** | 6-Speed Manual | 6-Speed Manual | 8-Speed Automatic | 5-Speed Manual |
| **Drivetrain** | FWD | FWD | HTRAC AWD | FWD |
| **Kerb Mass** | 1265 kg | 1175 kg | 1665 kg | 1010 kg |
| **GVW** | 1805 kg | 1680 kg | 2230 kg | 1440 kg |
| **Tyres** | 205/65 R16 | 205/65 R16 | 235/60 R18 | 185/65 R15 |

---

## License

This project is open-source under the MIT License. Feel free to use, modify, and distribute it for automotive engineering, academic studies, or commercial simulations.
