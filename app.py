from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Visi duomenys yra isgalvoti. Tai nera tikra OT/SCADA sistema.
TURBINES = [
    {"id": "VE-101", "site": "Siaures parkas", "status": "Veikia", "power_mw": 2.4},
    {"id": "VE-102", "site": "Siaures parkas", "status": "Veikia", "power_mw": 2.1},
    {"id": "VE-201", "site": "Vakaru parkas", "status": "Prieziura", "power_mw": 0.0},
    {"id": "VE-202", "site": "Vakaru parkas", "status": "Veikia", "power_mw": 2.7},
]


@app.get("/")
def dashboard():
    active = sum(turbine["status"] == "Veikia" for turbine in TURBINES)
    total_power = round(sum(turbine["power_mw"] for turbine in TURBINES), 1)
    return render_template(
        "index.html",
        turbines=TURBINES,
        active=active,
        total=len(TURBINES),
        power=total_power,
    )


@app.get("/api/turbines")
def turbines_api():
    return jsonify({"demo": True, "turbines": TURBINES})


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "vejoenergija-portal"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
