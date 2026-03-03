import numpy as np
import pandas as pd

# SCRIPT GENERUJE REÁLNÉ CHOVÁNÍ FIRMY, ZE KTERÉHO VYCHÁZEJÍ HLAVNÍ TABULKY: sensor_data, failures, maintenance

# =====================================================
# INITIAL MACHINE STATES
# =====================================================


def initialize_machine_states(machines):

    states = []

    for _, row in machines.iterrows():

        rng = np.random.default_rng()

        age_years = row["machine_age_years"]

        # 🔹 stáří zvyšuje degradaci
        age_factor = 1 + (age_years / 10)

        # základ degradace podle typu stroje
        if row["machine_type_id"] == 1:  # Řezací
            base = 0.00020
        elif row["machine_type_id"] == 2:  # Lis
            base = 0.00023
        elif row["machine_type_id"] == 3:  # Montáž
            base = 0.00018
        else:  # Test
            base = 0.00016

        base_degradation = base * age_factor

        # starší stroje mají vyšší threshold
        failure_threshold = 0.45 + (age_years / 50)

        states.append(
            {
                "machine_id": row["machine_id"],
                "line_id": row["line_id"],
                "machine_type_id": row["machine_type_id"],
                "health": 1.0,
                "base_degradation": base_degradation,
                "failure_threshold": failure_threshold,
                "is_running": True,
                "hours_since_maintenance": 0,
                "failure_remaining_hours": 0,
                "cooldown_remaining_hours": 0,
                "initial_age_hours": row["machine_age_years"] * 365 * 24,
                "simulated_hours": 0,
                "max_units_per_hour": row["max_units_per_hour"],
                "rng": rng,
            }
        )

    return states


# =====================================================
# MACHINE BEHAVIOUR PER HOUR
# =====================================================


def simulate_hour(state):

    # -----------------------------
    # MACHINE FAILURE ACTIVE
    # -----------------------------
    # cooldown odečítání
    if state["cooldown_remaining_hours"] > 0:
        state["cooldown_remaining_hours"] -= 1

    if state["failure_remaining_hours"] > 0:

        state["is_running"] = False
        state["failure_remaining_hours"] -= 1

        # porucha skončila → oprava
        if state["failure_remaining_hours"] == 0:

            recovery = state["rng"].uniform(0.25, 0.5)

            state["health"] = min(1.0, state["health"] + recovery)

            state["hours_since_maintenance"] = 0

            state["cooldown_remaining_hours"] = state["rng"].integers(12, 48)

    else:
        state["is_running"] = True

        # -----------------------------
        # NORMAL DEGRADATION
        # -----------------------------
        degradation = state["base_degradation"] * state["rng"].uniform(0.8, 1.2)

        state["health"] -= degradation
        state["health"] = max(state["health"], 0.05)

        state["hours_since_maintenance"] += 1

    state["simulated_hours"] += 1

    return state


# =====================================================
# SENSOR GENERATION
# =====================================================


def generate_sensor_values(state, timestamp):

    health = state["health"]
    rng = state["rng"]

    # ==================================
    # AMBIENT TEMPERATURE (FACTORY HALL)
    # ==================================

    day_of_year = timestamp.timetuple().tm_yday

    # venkovní sezónnost (-5 až 30)
    outside_temp = 12 + 18 * np.sin((day_of_year - 80) / 365 * 2 * np.pi)

    # hala tlumí vlivy prostředí
    ambient_temperature = (
        20  # základ haly
        + 0.25 * outside_temp  # jen část vlivu venku
        + rng.normal(0, 0.8)  # malé kolísání
    )

    # bezpečné limity haly
    ambient_temperature = np.clip(ambient_temperature, 15, 30)

    temperature = ambient_temperature + 30 + (1 - health) * 40 + rng.normal(0, 2)
    vibration = 2 + (1 - health) * 5 + rng.normal(0, 0.3)
    pressure = 5 + (1 - health) * 2 + rng.normal(0, 0.2)
    load = rng.uniform(60, 90)

    # bezpečné limity
    temperature = np.clip(temperature, 20, 120)
    vibration = np.clip(vibration, 0, 10)
    pressure = np.clip(pressure, 1, 10)
    load = np.clip(load, 0, 100)

    if state["is_running"]:
        performance_factor = rng.normal(0.92, 0.03)  # běžná odchylka výkonu
        performance_factor = np.clip(performance_factor, 0.75, 1.05)

        produced_units = int(state["max_units_per_hour"] * performance_factor)
    else:
        produced_units = 0

    produced_units = max(produced_units, 0)

    planned_production = state["max_units_per_hour"]

    # -----------------------
    # DEFECT RATE
    # -----------------------

    # základní scrap daného stroje (každý stroj má jiný baseline)
    base_defect_rate = rng.uniform(0.005, 0.02)  # 0.5 % – 2 %

    # degradace výrazně zvyšuje zmetkovitost
    degradation_effect = (1 - health) * 0.12

    # provozní náhodnost
    random_noise = rng.normal(0, 0.005)

    defect_rate = base_defect_rate + degradation_effect + random_noise

    # hranice 0–0.15 (0–15 %)
    defect_rate = np.clip(defect_rate, 0, 0.15)

    defective_units = int(produced_units * defect_rate)

    ok_units = produced_units - defective_units

    return {
        "temperature": temperature,
        "vibration": vibration,
        "pressure": pressure,
        "load": load,
        "ambient_temperature": ambient_temperature,
        "produced_units": produced_units,
        "planned_production": planned_production,
        "defective_units": defective_units,
        "ok_units": ok_units,
    }


# =====================================================
# FAILURE CHECK
# =====================================================


def check_failure(state, sensors):

    # ==========================================
    # 1️⃣ Pokud je zařízení už v poruše,
    #    nová porucha nesmí vzniknout
    # ==========================================
    # během cooldown nelze vzniknout porucha
    if state["cooldown_remaining_hours"] > 0:
        return False, 0, None

    if state["failure_remaining_hours"] > 0:
        return False, 0, None

    # ==========================================
    # 2️⃣ Kontrola threshold
    # ==========================================
    if state["health"] < state["failure_threshold"]:

        probability = (1 - state["health"]) * 0.18

        if state["rng"].random() < probability:

            duration = state["rng"].integers(2, 12)

            # ==========================================
            # 3️⃣ Výpočet skóre podle typu stroje
            # ==========================================

            temp_score = sensors["temperature"] / 100
            vib_score = sensors["vibration"] / 8
            press_score = sensors["pressure"] / 9

            machine_type = state["machine_type_id"]

            if machine_type == 1:  # Řezací
                scores = {
                    "mechanical": vib_score * 1.2,
                    "overheating": temp_score * 1.1,
                    "pressure": press_score * 0.8,
                    "electrical": 0.2,
                }

            elif machine_type == 2:  # Lis
                scores = {
                    "mechanical": vib_score * 1.5,
                    "overheating": temp_score * 0.9,
                    "pressure": press_score * 1.1,
                    "electrical": 0.2,
                }

            elif machine_type == 3:  # Montáž
                scores = {
                    "mechanical": vib_score * 1.1,
                    "overheating": temp_score * 0.8,
                    "pressure": press_score * 0.7,
                    "electrical": 0.4,
                }

            else:  # Testovací
                scores = {
                    "mechanical": vib_score * 0.7,
                    "overheating": temp_score * 0.8,
                    "pressure": press_score * 0.6,
                    "electrical": 0.8,
                }

            total = sum(scores.values())
            probabilities = [v / total for v in scores.values()]

            failure_type = state["rng"].choice(list(scores.keys()), p=probabilities)

            # ==========================================
            # 4️⃣ Aktivace poruchy
            # ==========================================
            state["failure_remaining_hours"] = duration

            # porucha zhorší health
            state["health"] *= state["rng"].uniform(0.7, 0.85)

            return True, duration, failure_type

    return False, 0, None


# =====================================================
# MAIN FACTORY SIMULATION
# =====================================================


def run_factory_simulation(machines, time_df):

    states = initialize_machine_states(machines)

    sensor_rows = []
    failures = []

    for _, time_row in time_df.iterrows():

        timestamp = time_row["timestamp"]
        shift_id = time_row["shift_id"]

        # ============================
        # ZPRACUJEME KAŽDOU LINKU ZVLÁŠŤ
        # ============================
        for line_id in set(s["line_id"] for s in states):

            # vezmeme stroje jedné linky
            line_states = [s for s in states if s["line_id"] == line_id]

            # seřadíme podle pořadí stanice (machine_type_id 1–4)
            line_states = sorted(line_states, key=lambda x: x["machine_type_id"])

            line_blocked = False

            for i, state in enumerate(line_states):

                # simulate hour přímo nad objektem
                simulate_hour(state)

                if line_blocked:
                    state["is_running"] = False

                    sensors = generate_sensor_values(state, timestamp)

                    sensors["produced_units"] = 0
                    sensors["defective_units"] = 0
                    sensors["ok_units"] = 0

                    failure_started = False
                    duration = 0
                    failure_type = None

                else:
                    sensors = generate_sensor_values(state, timestamp)

                    failure_started, duration, failure_type = check_failure(
                        state, sensors
                    )

                    if state["failure_remaining_hours"] > 0:
                        line_blocked = True

                # ---------------- SENSOR DATA ----------------
                sensor_rows.append(
                    {
                        "timestamp": timestamp,
                        "machine_id": state["machine_id"],
                        "line_id": state["line_id"],
                        "shift_id": shift_id,
                        "is_running": int(state["is_running"]),
                        "temperature": round(sensors["temperature"], 1),
                        "vibration": round(sensors["vibration"], 2),
                        "pressure": round(sensors["pressure"], 2),
                        "load": round(sensors["load"], 2),
                        "ambient_temperature": round(sensors["ambient_temperature"], 1),
                        "produced_units": sensors["produced_units"],
                        "defective_units": sensors["defective_units"],
                        "ok_units": sensors["ok_units"],
                        "planned_production": sensors["planned_production"],
                        "operating_hours_since_maintenance": state[
                            "hours_since_maintenance"
                        ],
                        "machine_age_hours": int(
                            state["initial_age_hours"] + state["simulated_hours"]
                        ),
                        "health_index": round(state["health"], 4),
                    }
                )

                # ---------------- FAILURE DATA ----------------
                if failure_started:
                    failures.append(
                        {
                            "machine_id": state["machine_id"],
                            "line_id": state["line_id"],
                            "failure_time": timestamp,
                            "downtime_hours": duration,
                            "failure_type": failure_type,
                        }
                    )

    sensor_df = pd.DataFrame(sensor_rows)
    failures_df = pd.DataFrame(failures)

    return sensor_df, failures_df
