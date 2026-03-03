import pandas as pd
from datetime import datetime, timedelta


def generate_D_Machine():

    today = datetime(2025, 1, 1)

    machines_data = [
        # machine_id, line_id, machine_type_id, name, manufacturer, age_years
        # ---------------- LINKA 1 ----------------
        (1, 1, 1, "L1 - Řezací stanice", "TRUMPF", 2),
        (2, 1, 2, "L1 - Lis", "SIEMENS", 3),
        (3, 1, 3, "L1 - Montážní stanice", "BOSCH", 5),
        (4, 1, 4, "L1 - Testovací stanice", "ABB", 6),
        # ---------------- LINKA 2 ----------------
        (5, 2, 1, "L2 - Řezací stanice", "TRUMPF", 1),
        (6, 2, 2, "L2 - Lis", "SIEMENS", 4),
        (7, 2, 3, "L2 - Montážní stanice", "BOSCH", 7),
        (8, 2, 4, "L2 - Testovací stanice", "ABB", 3),
        # ---------------- LINKA 3 ----------------
        (9, 3, 1, "L3 - Řezací stanice", "TRUMPF", 6),
        (10, 3, 2, "L3 - Lis", "SIEMENS", 2),
        (11, 3, 3, "L3 - Montážní stanice", "BOSCH", 8),
        (12, 3, 4, "L3 - Testovací stanice", "ABB", 5),
    ]

    machines = []

    for (
        machine_id,
        line_id,
        machine_type_id,
        machine_name,
        manufacturer,
        age_years,
    ) in machines_data:

        installation_date = today - timedelta(days=age_years * 365)

        # ================================
        # PARAMETRY PODLE TYPU STROJE
        # ================================

        if machine_type_id == 1:  # Řezací
            max_units_per_hour = 130
            acquisition_cost = 1500000
            depreciation_rate = 0.10
            expected_lifetime_hours = 100000
            hourly_production_loss = 32500

        elif machine_type_id == 2:  # Lis
            max_units_per_hour = 105
            acquisition_cost = 1350000
            depreciation_rate = 0.13
            expected_lifetime_hours = 85000
            hourly_production_loss = 26250

        elif machine_type_id == 3:  # Montáž
            max_units_per_hour = 95
            acquisition_cost = 1000000
            depreciation_rate = 0.12
            expected_lifetime_hours = 75000
            hourly_production_loss = 23750

        else:  # Testovací
            max_units_per_hour = 80
            acquisition_cost = 900000
            depreciation_rate = 0.14
            expected_lifetime_hours = 65000
            hourly_production_loss = 20000

        # ================================
        # KATEGORIZACE STÁŘÍ
        # ================================

        if age_years < 2:
            asset_age_id = 1
        elif age_years < 4:
            asset_age_id = 2
        elif age_years < 6:
            asset_age_id = 3
        else:
            asset_age_id = 4

        machines.append(
            {
                "machine_id": machine_id,
                "line_id": line_id,
                "machine_type_id": machine_type_id,
                "machine_name": machine_name,
                "manufacturer": manufacturer,
                "installation_date": installation_date.date(),
                "acquisition_cost": acquisition_cost,
                "depreciation_rate": depreciation_rate,
                "max_units_per_hour": max_units_per_hour,
                "planned_hours_per_day": 24,
                "hourly_production_loss": hourly_production_loss,
                "expected_lifetime_hours": expected_lifetime_hours,
                "machine_age_years": age_years,
                "asset_age_id": asset_age_id,
            }
        )

    df = pd.DataFrame(machines)
    df.to_csv("data/BI/D_Machine.csv", index=False)

    return df
