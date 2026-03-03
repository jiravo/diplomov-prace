import pandas as pd


def generate_D_MaintenanceType():

    data = [
        (1, "Preventivní"),
        (2, "Reaktivní"),
    ]

    df = pd.DataFrame(data, columns=["maintenance_type_id", "maintenance_type"])

    df.to_csv("data/BI/D_MaintenanceType.csv", index=False)

    return df
