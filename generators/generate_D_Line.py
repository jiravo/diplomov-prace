import pandas as pd


def generate_lines():

    lines = [
        {
            "line_id": 1,
            "line_name": "Linka 1",
            "plant": "Závod A",
            "description": "Automatizovaná výrobní a montážní linka – typ A",
        },
        {
            "line_id": 2,
            "line_name": "Linka 2",
            "plant": "Závod A",
            "description": "Automatizovaná výrobní a montážní linka – typ A",
        },
        {
            "line_id": 3,
            "line_name": "Linka 3",
            "plant": "Závod A",
            "description": "Automatizovaná výrobní a montážní linka – typ A",
        },
    ]

    df_lines = pd.DataFrame(lines)

    df_lines.to_csv("data/BI/D_Line.csv", index=False)

    return df_lines
