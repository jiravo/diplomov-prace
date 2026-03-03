import pandas as pd


def generate_asset_age():

    asset_age = [
        {
            "asset_age_id": 1,
            "age_bucket_name": "0–2 roky (Nové)",
            "age_min_years": 0,
            "age_max_years": 2,
        },
        {
            "asset_age_id": 2,
            "age_bucket_name": "2–4 roky (Stabilní)",
            "age_min_years": 2,
            "age_max_years": 4,
        },
        {
            "asset_age_id": 3,
            "age_bucket_name": "4–6 let (Stárnoucí)",
            "age_min_years": 4,
            "age_max_years": 6,
        },
        {
            "asset_age_id": 4,
            "age_bucket_name": "6+ let (Rizikové)",
            "age_min_years": 6,
            "age_max_years": 999,
        },
    ]

    df_asset_age = pd.DataFrame(asset_age)

    df_asset_age.to_csv("data/BI/D_AssetAge.csv", index=False)

    return df_asset_age
