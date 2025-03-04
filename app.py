from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import math

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return "Sag-Tension API is running!"

def calculate_total_weight(W_con, W_ice, W_wind):
    return math.sqrt((W_con + W_ice) ** 2 + W_wind ** 2)

def calculate_sag(S, W_total, T_h):
    return (W_total * S**2) / (8 * T_h)

@app.route('/calculate', methods=['GET'])
def calculate():
    try:
        S = float(request.args.get('span', 300))
        W_con = float(request.args.get('weight', 1.5))
        T_h = float(request.args.get('tension', 10000))
        W_ice = float(request.args.get('ice', 0.5))
        W_wind = float(request.args.get('wind', 0.3))

        # Step 1: Compute total weight
        W_total = calculate_total_weight(W_con, W_ice, W_wind)

        # Step 2: Compute sag
        sag = calculate_sag(S, W_total, T_h)

        # Step 3: Format LaTeX output
        latex_output = f"""
        \\[
        \\textbf{{Step-by-Step Calculations}}
        \\]

        \\[
        \\textbf{{1. Calculate Total Weight}} \\quad (W_{{total}})
        \\]

        \\[
        W_{{total}} = \\sqrt{{({W_con} + {W_ice})^2 + {W_wind}^2}}
        \\]

        \\[
        = \\sqrt{{({W_con + W_ice})^2 + {W_wind}^2}}
        \\]

        \\[
        = {round(W_total, 3)} \\quad \\text{{N/m}}
        \\]

        \\[
        \\textbf{{2. Apply Sag Formula}}
        \\]

        \\[
        \\text{{Sag}} = \\frac{{W_{{total}} \\times S^2}}{{8 \\times Tension}}
        \\]

        \\[
        = \\frac{{{round(W_total, 3)} \\times {S}^2}}{{8 \\times {T_h}}}
        \\]

        \\[
        = {round(sag, 3)} \\quad \\text{{meters}}
        \\]

        \\[
        \\textbf{{Final Result:}}
        \\]

        \\[
        \\text{{Total Weight}}: {round(W_total, 3)} \\quad \\text{{N/m}}
        \\]

        \\[
        \\text{{Sag}}: {round(sag, 3)} \\quad \\text{{meters}}
        \\]
        """

        return jsonify({
            "span": S,
            "weight_total": round(W_total, 3),
            "tension": T_h,
            "sag": round(sag, 3),
            "latex": latex_output
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
