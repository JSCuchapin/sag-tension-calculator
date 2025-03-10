from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import math
import numpy as np
from sympy import symbols, Eq, solve

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Function to calculate the weight due to wind
def calculate_weight_due_to_wind(Pressure, Diameter, thickness):
    return Pressure * (Diameter + 2 * thickness)

# Function to calculate total weight due to ice
def calculate_weight_due_ice(thickness, Diameter):
    density = 915  # Ice density in kg/m³
    return 9.81 * thickness * density * math.pi * (Diameter + thickness)

# Function to calculate total weight considering wind and ice
def calculate_total_weight(W_con, W_ice, W_wind):
    return math.sqrt((W_con + W_ice) ** 2 + W_wind ** 2)

# Function to calculate sag based on tension and weight
# Catenary Equation
def calculate_sag(S, W, H):
    sag = (H/W)*(math.cosh(S*W/2/H)-1)
    return sag if H > 0 else float('inf')

# Function to calculate blowout angle
def calculate_angle(W_ice, W_wind, W_con):
    theta = math.atan(W_wind/(W_ice+W_con))*180/3.14
    return theta

# Function to solve cubic equation for final tension using sympy
def calculate_final_tension(alpha, E, Area, W1, W2, S, H1, t1, t2):
    C1 = math.sqrt(E * Area / 24)
    C2 = alpha * E * Area
    A = C2 * (t2 - t1) + (W1 * S * C1 / H1) ** 2 - H1
    B = (W2 * S * C1) ** 2
    
    H2 = symbols('H2', real=True)
    equation = Eq(H2**3 + A * H2**2 - B, 0)
    roots = solve(equation, H2)
    real_roots = [float(r.evalf()) for r in roots if r.is_real and r > 0]
    
    return max(real_roots) if real_roots else float('nan'), C1, C2, A, B

@app.route('/conductors')
def get_conductors():
    return send_from_directory('static', 'conductors.json', mimetype='application/json')

@app.route('/calculate', methods=['GET'])
def calculate():
    try:
        S = float(request.args.get('span', 300))
        W_con = float(request.args.get('weight', 1.5)) * 9.81  
        H1 = float(request.args.get('initial_tension', 10000))
        t = float(request.args.get('ice_thickness', 0.05))
        Pressure = float(request.args.get('wind_pressure', 10))
        t1 = float(request.args.get('temp_initial', 25))
        t2 = float(request.args.get('temp_final', 40))
        alpha = float(request.args.get('Coefficient_Thermal_Expansion', 0.000019))
        E = float(request.args.get('modulus_elasticity', 79000000000))
        Area = float(request.args.get('cross_section_area', 0.000403225))
        Dia = float(request.args.get('diameter', 0.001))
        
        W_ice = calculate_weight_due_ice(t, Dia)
        W_wind = calculate_weight_due_to_wind(Pressure, Dia, t)
        W_total = calculate_total_weight(W_con, W_ice, W_wind)
        initial_sag = calculate_sag(S, W_con, H1)
        theta_deg = calculate_angle(W_ice,W_wind,W_con)
        theta_rad = theta_deg*3.14/180
        
        H2, C1, C2, A, B = calculate_final_tension(alpha, E, Area, W_con, W_total, S, H1, t1, t2)
        final_sag = calculate_sag(S, W_total, H2)
        final_horizontal_sag = final_sag*math.sin(theta_rad)
        final_vertical_sag = final_sag*math.cos(theta_rad)
        
        if math.isnan(H2) or H2 <= 0:
            H2 = "Calculation Error"
            final_sag = "Calculation Error"

        return jsonify({
            "span": float(S),
            "weight_total": round(float(W_total), 3),
            "initial_tension": float(H1),
            "final_tension": round(float(H2), 3) if isinstance(H2, (int, float)) and not math.isnan(H2) and not math.isinf(H2) else "Calculation Error",
            "initial_sag": round(float(initial_sag), 3),
            "final_sag": round(float(final_sag), 3) if isinstance(final_sag, (int, float)) else final_sag,
            "final_vertical_sag": round(float(final_vertical_sag), 3),
            "final_horizontal_sag": round(float(final_horizontal_sag), 3),
            "C1": round(float(C1), 3),
            "C2": round(float(C2), 6),
            "A": round(float(A), 3),
            "B": round(float(B), 3),
            "weight_ice": round(float(W_ice), 3),
            "weight_wind": round(float(W_wind), 3),
            "Blowout_angle": round(float(theta_deg), 3),
            "parameters": {
                "Coefficient_Thermal_Expansion": float(alpha),
                "Modulus_Elasticity": float(E),
                "Cross_Section_Area": float(Area),
                "Diameter": float(Dia),
                "Temperature_Initial": float(t1),
                "Temperature_Final": float(t2)
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
