from flask import Flask, request, jsonify
import math

app = Flask(__name__)

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

        W_total = calculate_total_weight(W_con, W_ice, W_wind)
        sag = calculate_sag(S, W_total, T_h)

        return jsonify({
            "span": S,
            "weight_total": round(W_total, 3),
            "tension": T_h,
            "sag": round(sag, 3)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

 
