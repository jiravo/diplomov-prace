import pandas as pd


def generate_machine_types():

    machine_types = [
        {
            "machine_type_id": 1,
            "machine_type_name": "Řezací stanice",
            "description": "Automatizovaná stanice pro dělení materiálu",
        },
        {
            "machine_type_id": 2,
            "machine_type_name": "Lis",
            "description": "Hydraulický lis pro tváření materiálu",
        },
        {
            "machine_type_id": 3,
            "machine_type_name": "Montážní stanice",
            "description": "Poloautomatická montážní operace",
        },
        {
            "machine_type_id": 4,
            "machine_type_name": "Testovací stanice",
            "description": "Kontrola kvality a funkční testování",
        },
    ]

    df_machine_types = pd.DataFrame(machine_types)

    df_machine_types.to_csv("data/BI/D_MachineType.csv", index=False)

    return df_machine_types
