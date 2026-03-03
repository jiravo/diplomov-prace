import numpy as np
import pandas as pd


# =====================================================
# INITIAL MACHINE STATES
# =====================================================


def initialize_machine_states(machines):

    states = []

    for _, row in machines.iterrows():

        rng = np.random.default_rng()

        age_years = rng.uniform(1, 12)

        age_factor = 1 + (age_years / 15)

        reliability_factor = rng.uniform(0.7, 1.2) * age_factor

        states.append(
            {
                "machine_id": row["machine_id"],
                "line_id": row["line_id"],
                "health": 1.0,
                # chronická spolehlivost
                "reliability_factor": reliability_factor,
                # čím vyšší factor → rychlejší degradace
                "base_degradation": rng.uniform(0.00018, 0.00035) * reliability_factor,
                # horší stroje mají vyšší threshold
                "failure_threshold": rng.uniform(0.45, 0.6) * reliability_factor,
                "is_running": True,
                "hours_since_maintenance": 0,
                "failure_remaining_hours": 0,
                "cooldown_remaining_hours": 0,
                "age_years": age_years,
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
        produced_units = int(rng.normal(80 * state["health"], 5))
    else:
        produced_units = 0

    produced_units = max(produced_units, 0)

    return {
        "temperature": temperature,
        "vibration": vibration,
        "pressure": pressure,
        "load": load,
        "ambient_temperature": ambient_temperature,
        "produced_units": produced_units,
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
            # 3️⃣ Výpočet skóre podle senzorů
            # ==========================================
            temp_score = sensors["temperature"] / 100
            vib_score = sensors["vibration"] / 8
            press_score = sensors["pressure"] / 9

            scores = {
                "mechanical": vib_score,
                "overheating": temp_score,
                "pressure": press_score,
                "electrical": 0.2,  # baseline
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

        for state in states:

            state = simulate_hour(state)

            sensors = generate_sensor_values(state, timestamp)

            failure_started, duration, failure_type = check_failure(state, sensors)

            # ---------------- SENSOR DATA ----------------
            sensor_rows.append(
                {
                    "timestamp": timestamp,
                    "machine_id": state["machine_id"],
                    "line_id": state["line_id"],
                    "shift_id": shift_id,
                    "is_running": int(state["is_running"]),
                    "temperature": sensors["temperature"],
                    "vibration": sensors["vibration"],
                    "pressure": sensors["pressure"],
                    "load": sensors["load"],
                    "ambient_temperature": sensors["ambient_temperature"],
                    "produced_units": sensors["produced_units"],
                    "operating_hours_since_maintenance": state[
                        "hours_since_maintenance"
                    ],
                    "health_index": state["health"],
                }
            )

            # ---------------- FAILURE LOG ----------------
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
