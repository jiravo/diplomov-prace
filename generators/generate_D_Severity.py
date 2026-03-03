import pandas as pd


def generate_D_Severity():

    data = [
        (1, "Nízká", "Krátkodobá porucha bez významného dopadu na výrobu"),
        (2, "Střední", "Porucha vyžadující zásah údržby a částečné omezení výroby"),
        (3, "Vysoká", "Kritická porucha s výrazným dopadem na výrobu"),
    ]

    df = pd.DataFrame(
        data, columns=["severity_id", "severity_level", "severity_description"]
    )

    df.to_csv("data/BI/D_Severity.csv", index=False)

    return df
